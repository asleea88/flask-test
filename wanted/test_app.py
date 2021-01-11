import os
import tempfile
import pytest
import settings
from models import db, Company, TagName, Tag
from app import app


@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def test_search_name(client):
    rsp = client.get(
        '/searches/companies/name/', query_string={'name': 'want'}
    )
    assert rsp.status_code == 200
    assert rsp.json['companies'][0]['name'] == '원티드랩'

    rsp = client.get(
        '/searches/companies/name/', query_string={'name': 'ante'}
    )
    assert rsp.status_code == 200
    assert rsp.json['companies'][0]['name'] == '원티드랩'


def test_search_name_bad_request(client):
    rsp = client.get(
        '/searches/companies/name/', query_string={'name': ''}
    )
    assert rsp.status_code == 400

    rsp = client.get(
        '/searches/companies/name/',
        query_string={'name': 'a' * (settings.COMPANY_NAME_MAX_LEN + 1)}
    )
    assert rsp.status_code == 400


def test_search_tags_full_match(client):
    with app.app_context():
        company = Company.get_from_name(db.session, 'en', 'Wantedlab')
        tags = company.get_tags(db.session)

    tag_ids = list(map(lambda x: str(x.id), tags))
    tag_ids_param = ','.join(tag_ids)

    rsp = client.get('/searches/companies/tag/', query_string={'tags': tag_ids_param})
    assert rsp.status_code == 200
    assert rsp.json['companies'][0] == {'id': company.id, 'name': '원티드랩'}


def test_search_tag_partial_match(client):
    with app.app_context():
        company = Company.get_from_name(db.session, 'en', 'Wantedlab')
        tags = company.get_tags(db.session)[:1]

    tag_ids = list(map(lambda x: str(x.id), tags))
    tag_ids_param = ','.join(tag_ids)

    rsp = client.get('/searches/companies/tag/', query_string={'tags': tag_ids_param})
    assert rsp.status_code == 200
    assert len(rsp.json['companies']) == 5
    filter_obj = filter(
        lambda x: x['id'] == company.id, rsp.json['companies']
    )
    assert len(list(filter_obj)) == 1


def test_add_company_tags(client):

    with app.app_context():
        company = Company.get_from_name(db.session, 'en', 'Wantedlab')
        tag_29 = Tag.get_from_name(db.session, 'en', 'tag_29')
        tag_30 = Tag.get_from_name(db.session, 'en', 'tag_30')

    body = {'tags': [{'id': tag_29.id}, {'id': tag_30.id}]}
    rsp = client.post(
        f'/companies/{company.id}/tags/', json=body
    )
    assert rsp.status_code == 200

    with app.app_context():
        company_tags = company.get_tags(db.session)

    company_tag_ids = set(map(lambda x: x.id, company_tags))
    assert set([tag_29.id, tag_30.id]).issubset(company_tag_ids)

    # 중복 태그 생성 요청
    rsp = client.post(
        f'/companies/{company.id}/tags/', json=body
    )
    assert rsp.status_code == 403


def test_add_company_tags_bad_request(client):
    rsp = client.post(
        '/companies/1/tags/', data='test'
    )
    assert rsp.status_code == 400

    body = {'tags': [{'id': -1}, {'id': 10}]}
    rsp = client.post(
        '/companies/1/tags/', json=body
    )
    assert rsp.status_code == 400


def test_delete_company_tags(client):

    with app.app_context():
        company = Company.get_from_name(db.session, 'en', 'Wantedlab')
        tags = company.get_tags(db.session)[1:]

    rsp = client.delete(
        f'/companies/{company.id}/tags/',
        query_string={'tags': f'{tags[0].id}'}
    )
    assert rsp.status_code == 200

    with app.app_context():
        company_tags = company.get_tags(db.session)

    company_tag_ids = set(map(lambda x: x.id, company_tags))
    assert not set([tags[0].id]).issubset(company_tag_ids)
