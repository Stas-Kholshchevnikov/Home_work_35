from django.core.management import BaseCommand
import logging
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import GoalCategory, BoardParticipant, Goal

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("start bot")

user_states = {'state': {}}
cat_id = []
logger.info(user_states)
logger.info(cat_id)

class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
    def handle(self, *args, **options):
        offset = 0
        self.stdout.write(self.style.SUCCESS('Bot started'))
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)
                # self.tg_client.send_message(chat_id=item.message.chat.id, text=item.message.text)


    def handle_message(self, msg: Message):
        # self.tg_client.send_message(chat_id=msg.chat.id, text=msg.text)
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id, defaults={'username': msg.chat.username})
        if "/start" in msg.text:
            self.tg_client.send_message(
                msg.chat.id, "Приветствую!\n"
                             'Доступные команды:\n'
                             '/board -> выводит список досок задач\n'
                             '/category -> выводит список категорий\n'
                             '/goals -> выводит список целей\n'
            )
        if tg_user.is_verified:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        #if msg.text.startswith('/'):
        #self.tg_client.send_message(msg.chat.id, 'Gud Morning im sky_pd_bot!')
        """ Для работы с верифицированным пользователем.
                Принимает и обрабатывает следующие команды:
                :param: /goals -> выводит список целей
                :param: /create -> позволяет создавать новые цели
                :param: /cancel -> позволяет отменить создание цели (только на этапе создания)
                :param: /category -> выводит список категорий
                :param: /board -> выводит список досок задач
                :param: /choose -> позволяет сделать выбор категории
                """
        allowed_commands = ['/goals', '/create', '/cancel']

        if not msg.text:
            return
        if "/start" in msg.text:
            return
        if "/board" in msg.text:
            self.fetch_board(msg, tg_user)
        elif '/category' in msg.text:
            self.fetch_category(msg, tg_user)
        elif '/goals' in msg.text:
            self.fetch_tasks(msg, tg_user)
        elif '/create' in msg.text:
            self.handle_categories(msg, tg_user)
        elif '/cancel' in msg.text:
            self.get_cancel(msg, tg_user)

        elif ('user' not in user_states['state']) and (msg.text not in allowed_commands):
            self.tg_client.send_message(tg_user.chat_id, 'Unknown command')

        elif (msg.text not in allowed_commands) and (
                user_states['state']['user']
        ) and (
                'category' not in user_states['state']
        ):
            category = self.handle_save_category(msg, tg_user)
            if category:
                user_states['state']['category'] = category
                self.tg_client.send_message(
                    tg_user.chat_id, f'Выбрана категория:\n {category}.\nВведите заголовок цели.'
                )

        elif (msg.text not in allowed_commands) and (
                user_states['state']['user']
        ) and (user_states['state']['category']) and (
                'goal_title' not in user_states['state']
        ):
            user_states['state']['goal_title'] = msg.text
            logger.info(user_states)
            goal = Goal.objects.create(
                title=user_states['state']['goal_title'],
                user=user_states['state']['user'],
                category=user_states['state']['category'],
            )
            self.tg_client.send_message(tg_user.chat_id, f'Цель: {goal} создана в БД')
            del user_states['state']['user']
            del user_states['state']['msg_chat_id']
            del user_states['state']['category']
            del user_states['state']['goal_title']
            cat_id.clear()

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        self.tg_client.send_message(tg_user.chat_id, "Hello! Please authorized for begin use bot!")
        tg_user.update_verification_code()
        tg_user.save(update_fields=["verification_code"])
        self.tg_client.send_message(tg_user.chat_id, f"Your code verification: {tg_user.verification_code}")

    def fetch_board(self, msg: Message, tg_user: TgUser):
        """ Список Досок участника"""
        boards = BoardParticipant.objects.filter(user=tg_user.user)

        if boards:
            [self.tg_client.send_message(
                msg.chat.id, f"Ваши доски: {item.board.title}\n"
            ) for item in boards if item.board.is_deleted is not True]
        else:
            self.tg_client.send_message(msg.chat.id, "Доски отсутствуют.")

    def fetch_category(self, msg: Message, tg_user: TgUser):
        """
        Вывод категорий пользователя в ТГ-бот.
        """
        resp_categories: list[str] = [
            f'{category.id} {category.title}'
            for category in GoalCategory.objects.filter(
                board__participants__user=tg_user.user_id, is_deleted=False)]
        if resp_categories:
            self.tg_client.send_message(
                msg.chat.id, "Ваши категории\n===================\n" + '\n'.join(resp_categories)
            )
        else:
            self.tg_client.send_message(msg.chat.id, 'У Вас нет созданных категории!')

    def handle_categories(self, msg: Message, tg_user: TgUser):
        """
         Выбор ID категории для сохранения цели
        """
        categories = GoalCategory.objects.filter(user=tg_user.user)
        if categories.count() > 0:
            cat_text = ''
            for cat in categories:
                cat_text += f'{cat.id}: {cat.title} \n'
                cat_id.append(cat.id)
            self.tg_client.send_message(
                chat_id=tg_user.chat_id,
                text=f'Выберите номер категории:\n{cat_text}'
                     f'Для отмены введите: /cancel'
            )
            if 'user' not in user_states['state']:
                user_states['state']['user'] = tg_user.user
                user_states['state']['msg_chat_id'] = tg_user.chat_id
                logger.info(user_states)
        else:
            self.tg_client.send_message(msg.chat.id, 'Category not found!')

    def fetch_tasks(self, msg: Message, tg_user: TgUser):
        """
        Получение целей из БД и отправка на вывод в ТГ-бот
        """
        goals = Goal.objects.filter(user=tg_user.user)
        if goals.count() > 0:
            [self.tg_client.send_message(tg_user.chat_id,
                                         f'Название: {goal.title},\n'
                                         f'Категория: {goal.category},\n'
                                         f'Статус: {goal.get_status_display()},\n'
                                         f'Пользователь: {goal.user},\n'
                                         f'Дедлайн {goal.due_date if goal.due_date else "Нет"} \n') for goal in goals]
        else:
            self.tg_client.send_message(msg.chat.id, 'Goals not found!')

    @staticmethod
    def handle_save_category(msg: Message, tg_user: TgUser):
        """ Обрабатыватывает категории для сохранения """
        category_id = int(msg.text)
        category_data = GoalCategory.objects.filter(user=tg_user.user).get(pk=category_id)
        return category_data

    def get_cancel(self, msg: Message, tg_user: TgUser):
        if 'user' in user_states['state']:
            del user_states['state']['user']
            del user_states['state']['msg_chat_id']

            if 'category' in user_states['state']:
                del user_states['state']['category']

            if 'goal_title' in user_states['state']:
                del user_states['state']['goal_title']
        self.tg_client.send_message(tg_user.chat_id, 'Cancel')