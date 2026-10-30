"""Functional contract: persistence, patient isolation and role permissions."""
import os

os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-production-123456789")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.security import hash_password, token_for


@pytest.fixture()
def environment(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    make_session = sessionmaker(engine, expire_on_commit=False)
    with make_session() as db:
        users = {}
        for role in ("doctor", "nurse", "lab", "admin"):
            user = models.StaffUser(email=f"{role}@test.local", password_hash=hash_password("testing-password"), role=role)
            db.add(user); db.flush(); users[role] = user
        a = models.Patient(name="Synthetic Patient A")
        b = models.Patient(name="Synthetic Patient B")
        db.add_all([a,b]);db.flush()
        observation = models.Observation(patient_id=a.id,code="hb",label="Hemoglobin",value_num=11.4,unit="g/dL")
        db.add(observation);db.commit()
        aid,bid,oid=a.id,b.id,observation.id
        tokens={role:token_for(user) for role,user in users.items()}

    def override():
        with make_session() as session:
            yield session
    app.dependency_overrides[get_db] = override
    yield TestClient(app),tokens,aid,bid,oid
    app.dependency_overrides.clear()
    engine.dispose()


def headers(tokens, role):
    return {"Authorization": f"Bearer {tokens[role]}"}


def test_verify_correct_and_audit(environment):
    client,tokens,pid,_,oid = environment
    path=f"/reviews/patients/{pid}"
    original=client.get(path,headers=headers(tokens,"doctor"))
    assert original.status_code==200
    assert original.json()["observations"][0]["verified"] is False
    verified=client.post(path,headers=headers(tokens,"doctor"),json={"target_type":"observation","target_id":str(oid),"decision":"verified","reason":"Compared with source"})
    assert verified.status_code==201, verified.text
    corrected=client.post(path,headers=headers(tokens,"doctor"),json={"target_type":"observation","target_id":str(oid),"decision":"corrected","reason":"Source reads 11.8","corrected_value_num":11.8})
    assert corrected.status_code==201,corrected.text
    assert corrected.json()["before"]["value_num"]==11.4
    assert corrected.json()["after"]["value_num"]==11.8
    data=client.get(path,headers=headers(tokens,"doctor")).json()
    assert data["observations"][0]["value_num"]==11.8
    assert len(data["history"])==2
    assert data["observations"][0]["review"]["decision"]=="corrected"


def test_role_and_patient_protection(environment):
    client,tokens,pid,other,oid=environment
    path=f"/reviews/patients/{pid}"
    payload={"target_type":"observation","target_id":str(oid),"decision":"verified","reason":"Source examined"}
    assert client.post(path,json=payload).status_code==401
    assert client.post(path,headers=headers(tokens,"admin"),json=payload).status_code==403
    assert client.post(f"/reviews/patients/{other}",headers=headers(tokens,"doctor"),json=payload).status_code==404
    invalid={"target_type":"checklist","target_id":"none","decision":"reviewed","reason":"No document"}
    assert client.post(path,headers=headers(tokens,"lab"),json=invalid).status_code==403
    assert client.post(path,headers=headers(tokens,"nurse"),json={**payload,"decision":"corrected"}).status_code==422
    assert client.post(path,headers=headers(tokens,"lab"),json=payload).status_code==201


def test_audio_requires_explicit_consent_and_key(environment):
    client,tokens,_,_,_=environment
    endpoint="/workflow/transcribe"
    headers_doctor=headers(tokens,"doctor")
    audio={"file":("demo.wav",b"RIFF"+b"0"*100,"audio/wav")}
    without_consent=client.post(endpoint,headers=headers_doctor,files=audio,data={"language":"en","synthetic_consent":"false"})
    assert without_consent.status_code==422
    without_key=client.post(endpoint,headers=headers_doctor,files=audio,data={"language":"en","synthetic_consent":"true"})
    assert without_key.status_code==503
    no_lab=client.post(endpoint,headers=headers(tokens,"lab"),files=audio,data={"language":"en","synthetic_consent":"true"})
    assert no_lab.status_code==403


def test_unlogged_edits_disabled(environment):
    client,tokens,_,_,oid=environment
    r=client.patch(f"/observations/{oid}",headers=headers(tokens,"doctor"),json={"value_num":12.2})
    assert r.status_code==410
