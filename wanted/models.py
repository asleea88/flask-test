import settings

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()


class Company(db.Model):
    # 회사 정보를 저장한다.
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def create_company(cls, session, default_language=None, default_name=None):
        company = cls()

        if default_language is not None:
            compnay_name = CompanyName(
                language=default_language, name=default_name
            )
            company.company_names.append(compnay_name)

        session.add(company)
        return company

    @classmethod
    def get_from_name(cls, session, language, name):
        return session.query(
            Company
        ).join(
            CompanyName
        ).filter(
            CompanyName.language == language, CompanyName.name == name
        ).one()

    def get_tags(self, session):
        return session.query(
            Tag
        ).join(
            CompanyTag
        ).filter(
            CompanyTag.company_id == self.id
        ).all()

    def append_name(self, session, language, name):
        company_name = CompanyName(language=language, name=name, company=self)
        session.add(company_name)

    def append_tag(self, session, tag):
        # TODO: tag.id
        company_tag = CompanyTag(company=self, tag=tag)
        session.add(company_tag)


class CompanyName(db.Model):
    # 언어별 회사 이름을 저장한다.
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    language = db.Column(db.String(settings.LANGUAGE_MAX_LEN))
    name = db.Column(db.String(settings.COMPANY_NAME_MAX_LEN), index=True)

    company = db.relationship(
        'Company', backref=db.backref('company_names', lazy=True)
    )


class CompanyTag(db.Model):
    # 회사가 포함하고 있는 태그 정보를 저장한다.
    id = db.Column(db.Integer, primary_key=True)

    #company_id는unique constraint index 사용
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), index=True)

    tag = db.relationship(
        'Tag', backref=db.backref('compnay_tags', lazy=True)
    )
    company = db.relationship(
        'Company', backref=db.backref('company_tags', lazy=True)
    )

    __table_args__ = (
        UniqueConstraint('company_id', 'tag_id', name='_compnay_tag_unique'),
    )


class Tag(db.Model):
    # 태그 정보를 저장한다.
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def create_tag(cls, session, default_language=None, default_name=None):
        tag = cls()

        if default_language is not None:
            tag_name = TagName(
                name=default_name, language=default_language
            )
            tag.tag_names.append(tag_name)

        session.add(tag)
        return tag

    @classmethod
    def get_from_name(cls, session, language, name):
        return session.query(
            Tag
        ).join(
            TagName
        ).filter(
            TagName.language == language, TagName.name == name
        ).one()

    def append_tag_name(self, session, language, name):
        tag_name = TagName(name=name, language=language, tag=self)
        session.add(tag_name)


class TagName(db.Model):
    # 언어별 태그 이름정보를 저장한다.
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    name = db.Column(db.String(settings.TAG_NAME_MAX_LEN))
    language = db.Column(db.String(settings.LANGUAGE_MAX_LEN))

    tag = db.relationship(
        'Tag', backref=db.backref('tag_names', lazy=True)
    )

    __table_args__ = (
        UniqueConstraint('tag_id', 'language', name='_tag_language_unique'),
    )

    def __repr__(self):
        return '<TagName %r %r>' % (self.language, self.name)
