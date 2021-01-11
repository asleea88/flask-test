from flask import request, Blueprint
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from models import db, Company, CompanyTag, CompanyName
from helpers import parse_str_list
from schemas import CompanyNameArgs, AddCompanyTagReq, TagIdsArgs
from pydantic import ValidationError
import settings

wanted_api = Blueprint('wanted_api', __name__)


@wanted_api.route('/health/', methods=['GET'])
def health():
    return '', 200


@wanted_api.route('/searches/companies/name/', methods=['GET'])
def search_company_name():
    '''
    ElasticSearch를 사용하면 더 효과적인 검색이 가능하다.
    '''
    try:
        company_name = CompanyNameArgs(value=request.args.get('name')).value
    except ValidationError:
        return '', 400

    # SQLite의 Like는 대소문자를 구분하지 않는다 (Case-insensitive).
    subquery_obj = db.session.query(CompanyName.company_id).filter(
        CompanyName.name.like(f'%{company_name}%')
    ).subquery()

    query_obj = db.session.query(
        CompanyName.company_id, CompanyName.name
    ).filter(
        CompanyName.company_id == subquery_obj.c.company_id,
        CompanyName.language == settings.SERVICE_COUNTRY
    )

    companies = []

    for company_name in query_obj.all():    # Emit SQL
        company_id, company_name = company_name
        companies.append({'id': company_id, 'name': company_name})

    return {'companies': companies}, 200


@wanted_api.route('/searches/companies/tag/', methods=['GET'])
def search_company_tag():
    try:
        tag_ids = TagIdsArgs(value=request.args.get('tags')).value[:3]
    except ValidationError:
        return '', 400

    query_obj = db.session.query(
        Company.id, CompanyName.name
    ).join(
        CompanyTag
    ).join(
        CompanyName
    ).filter(
        CompanyTag.tag_id.in_(tag_ids),
        CompanyName.language == settings.SERVICE_COUNTRY
    ).group_by(
        Company.id
    ).having(
        func.count(Company.id) == len(tag_ids)
    )

    companies = []

    for company in query_obj.all():     # Emit SQL
        company_id, company_name = company
        companies.append({'id': company_id, 'name': company_name})

    return {'companies': companies}, 200


@wanted_api.route('/companies/<int:company_id>/tags/', methods=['POST'])
def add_company_tag(company_id):
    try:
        request_json_ = {} if request.json is None else request.json
        request_json = AddCompanyTagReq(**request_json_).dict()
    except ValidationError:
        return '', 400

    tags = request_json['tags']
    company_id = int(company_id)

    for tag in tags:
        company_tag = CompanyTag(company_id=company_id, tag_id=tag['id'])
        db.session.add(company_tag)

    try:
        db.session.commit()     # Emit SQL
    except IntegrityError:
        return '', 403

    return '', 200


@wanted_api.route('/companies/<int:company_id>/tags/', methods=['DELETE'])
def remove_company_tag(company_id):
    try:
        tag_ids = TagIdsArgs(value=request.args.get('tags')).value
    except ValidationError:
        return '', 400

    company_id = int(company_id)

    db.session.query(
        CompanyTag
    ).filter(
        CompanyTag.company_id == company_id, CompanyTag.tag_id.in_(tag_ids)
    ).delete(synchronize_session=False)     # Emit SQL

    return '', 200
