from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class InlineCheckBox(InlineKeyboardMarkup):

    def __init__(self, dict_buts, check_box=['⬜', '✅'], accept_text='➡ Принять', accept_callback='Accept', row_width=1,
                 **kwargs):
        """
        Создание чек-бокса
        :dict_buts: dict: key=callback_data, value = Текст кнопки
        :check_box: list: [0] - unCheck, [1] - Check
        :acept_text: str: Текст кнопки сохранения результата
        """
        self.dict_buts = dict_buts
        self.check_box = check_box
        self.inline_acept = InlineKeyboardButton(text=accept_text, callback_data=accept_callback)
        self.row_width_check = row_width
        super(InlineCheckBox, self).__init__(row_width=row_width, inline_keyboard=None, **kwargs)
        self.buttons_fill()

    def buttons_fill(self):
        """
        метод заполнения чек-бокса
        """
        buts = []

        for key, value in self.dict_buts.items():
            buts.append(InlineKeyboardButton(text=(self.check_box[0] + ' ' + value), callback_data=key))

        if len(buts) == 1:
            self.add(*buts)
        elif len(buts) % 2 == 0:
            for index in range(0, len(buts), 2):
                self.row(buts[index], buts[index + 1])
        elif not buts:
            return None
        else:
            for index in range(0, len(buts) - 1, 2):
                self.row(buts[index], buts[index + 1])
            self.add(buts[-1])
        return self.insert(self.inline_acept)

    def buttons_fill_callback(self, callback, chek: str = None):
        """
        метод заполнения чек_бокса, с учетом нажатия на кнопку
        """
        buts = []
        chek_count = 0
        row_count = 0
        button_count = 0
        inl_answer = InlineKeyboardMarkup(row_width=self.row_width_check)
        if not chek:
            for key, value in self.dict_buts.items():
                if callback.data == key:
                    buts.append(InlineKeyboardButton(text=(self.check_box[0 if self.check_box[1] in
                                                                               callback.message.reply_markup.inline_keyboard[
                                                                                   row_count][
                                                                                   button_count % 2].text else 1] + ' ' + value),
                                                     callback_data=key))
                else:
                    buts.append(InlineKeyboardButton(
                        text=callback.message.reply_markup.inline_keyboard[row_count][button_count % 2].text,
                        callback_data=key))

                if button_count % 2 == 1:
                    row_count += 1
                button_count += 1
        else:
            for key, value in self.dict_buts.items():
                buts.append(
                    InlineKeyboardButton(text=(self.check_box[int(chek[chek_count])] + ' ' + value), callback_data=key))
                chek_count += 1

        if len(buts) == 1:
            inl_answer.add(*buts)
        elif len(buts) % 2 == 0:
            for index in range(0, len(buts), 2):
                inl_answer.row(buts[index], buts[index + 1])
        elif not buts:
            return None
        else:
            for index in range(0, len(buts) - 1, 2):
                inl_answer.row(buts[index], buts[index + 1])
            inl_answer.add(buts[-1])

        return inl_answer.insert(self.inline_acept)

    def get_result(self, callback):

        result_acept = []
        row_count_acept = 0
        button_count_acept = 0

        for _ in range(len(self.dict_buts)):
            if self.check_box[1] in callback.message.reply_markup.inline_keyboard[row_count_acept][button_count_acept % 2].text:
                result_acept.append('1')
            else:
                result_acept.append('0')

            if button_count_acept % 2 == 1:
                row_count_acept += 1
            button_count_acept += 1

        return result_acept
