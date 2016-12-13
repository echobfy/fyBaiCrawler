# -*- coding: utf-8 -*-

import xlwt


class ExcelWriter(object):

    def __init__(self, file_name="records.xls"):
        self.file_name = file_name
        self.fp = xlwt.Workbook(encoding='utf-8')

        self.name2sheet = {}

    def ensure_sheet(self, sheet_name, origin_column=1):
        if self.name2sheet.get(sheet_name):
            return self.name2sheet[sheet_name]
        else:
            sheet = self.fp.add_sheet(sheet_name)
            self.name2sheet[sheet_name] = (sheet, origin_column)
            return self.name2sheet[sheet_name]

    def write_head(self, sheet_name, args=()):
        sheet, index = self.ensure_sheet(sheet_name)
        for i, arg in enumerate(args):
            sheet.write(0, i, arg)

    def write_record(self, sheet_name, requested_index=None, args=()):
        sheet, index = self.ensure_sheet(sheet_name, 0)
        index = requested_index if requested_index else index
        for i, arg in enumerate(args):
            sheet.write(index, i, arg)

        index += 1
        self.name2sheet[sheet_name] = [sheet, index]

    def close(self):
        self.fp.save(self.file_name)


# just for Test
if __name__ == '__main__':
    excel_writer = ExcelWriter()
    excel_writer.write_head("视频", args=("app", "备注"))
    excel_writer.write_head("金融", args=("app", "地址"))

    excel_writer.write_record("视频", args=("爱奇艺", "是个视频网站"))
    excel_writer.write_record("视频", args=("土豆", "感觉快挂了"))
    excel_writer.write_record("金融", args=("挖财", "杭州"))
    excel_writer.write_record("金融", args=("陆金所", "上海"))

    excel_writer.close()

