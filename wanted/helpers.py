import csv
from models import Company, CompanyName, CompanyTag, Tag, TagName, db
from sqlalchemy.orm import sessionmaker


class DatabaseInitialzier:

    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.session = db.session

    def init_tags(self):
        language_list = [('en', 'tag'), ('ko', '태그'), ('ja', 'タグ')]
        for i in range(30):
            tag = Tag.create_tag(self.session)
            for language, name in language_list:
                tag.append_tag_name(self.session, language, f'{name}_{i + 1}')

    def init_companies(self):
        with open(self.csv_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            col_info = None

            for row in csv_reader:

                if csv_reader.line_num == 1:
                    col_info = row
                    continue

                self.init_company(col_info, row)

    def init_company(self, col_info, row):
        company = Company()

        for i, data in enumerate(row):

            category, language = col_info[i].split('_')

            if (category == 'company'):

                if data == '':
                    continue

                company.append_name(self.session, language, data)

            elif category == 'tag':
                if language == 'en':
                    tag_names = data.split('|')
                    for tag_name in tag_names:
                        tag = self.session.query(
                            Tag
                        ).join(
                            TagName
                        ).filter(
                            (TagName.language == language) & (TagName.name == tag_name)
                        ).one()
                        company.append_tag(self.session, tag)

            else:
                raise Exception(f'Unexpected column({col_info[i]})')

            self.session.add(company)

    def init(self):
        self.init_tags()
        self.init_companies()
        self.session.commit()


def parse_str_list(str_value, delimiter=','):
    try:
        return list(map(lambda x: int(x), str_value.split(delimiter)))
    except Exception:
        return


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    database_initializer = DatabaseInitialzier('wanted_temp_data.csv')
    database_initializer.init()
