# Отчет по лабораторной работе №1

Выполнил: Акулов Алексей, K33391

#### Цель работы:

Реализовать полноценное серверное приложение с помощью фреймворка FastAPI с применением дополнительных средств и библиотек

## Задание

### Текст задания:

Необходиом создать простой сервис для управления личными финансами.
Сервис должен позволять пользователям вводить доходы и расходы, устанавливать бюджеты на различные категории,
а также просматривать отчеты о своих финансах.
Дополнительные функции могут включать в себя возможность получения уведомлений о превышении бюджета,
анализа трат и установки целей на будущее.

#### Реализация моделей:

```
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(index=True)
    password: str
    balance: Optional["Balance"] = Relationship(back_populates="user")
    created_at: datetime.datetime = Field(default=datetime.datetime.now())


class UserInput(SQLModel):
    username: str
    password: str
    password2: str

    @validator('password2')
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords don\'t match')
        return v


class UserLogin(SQLModel):
    username: str
    password: str


class Balance(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="balance")
    total_budget: int = Field(default=0)
    saving_target: int = Field(default=0)
    categories: List["Category"] = Relationship(back_populates="balance")


class Category(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    limit: Optional[int] = None
    balance_id: int = Field(foreign_key="balance.id")
    balance: Balance = Relationship(back_populates="categories")
    transactions: List["Transaction"] = Relationship(back_populates="category")


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(SQLModel, table=True):
    id: int = Field(primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="transactions")
    type: TransactionType
    value: int
    created_at: datetime.datetime = Field(default=datetime.datetime.now())


class TransactionsCreate(SQLModel):
    category_id: int
    type: TransactionType
    value: int


class TransactionsUpdate(SQLModel):
    category_id: int
    type: TransactionType
    value: int


class TransactionRead(SQLModel):
    id: int
    category_id: int
    type: TransactionType
    value: int
    created_at: datetime.datetime


class CategoryRead(SQLModel):
    id: int
    name: str
    limit: Optional[int]
    transactions: List[TransactionRead]


class BalanceRead(SQLModel):
    id: int
    total_budget: int
    saving_target: int
    categories: List[CategoryRead]


class UserRead(SQLModel):
    id: int
    username: str
    balance: BalanceRead
    created_at: datetime.datetime
```


#### Реализация энпоинтов:

```
main_router = APIRouter()

@main_router.get("/users/{user_id}", response_model=UserRead)
def get_user_with_balance_and_categories(user_id: int):
    user = (session.query(User)
            .options(joinedload(User.balance)
                     .joinedload(Balance.categories)
                     .joinedload(Category.transactions))
            .filter(User.id == user_id)
            .first())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@main_router.get("/balances/{user_id}", response_model=BalanceRead)
def get_balance_with_categories(user_id: int):
    balance = (session.query(Balance)
               .options(joinedload(Balance.categories)
                        .joinedload(Category.transactions))
               .filter(Balance.user_id == user_id)
               .first())
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance

@main_router.get("/categories/{category_id}", response_model=CategoryRead)
def get_category_with_transactions(category_id: int):
    category = (session.query(Category)
                .options(joinedload(Category.transactions))
                .filter(Category.id == category_id)
                .first())
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@main_router.post("/transactions/", response_model=TransactionRead)
def create_transaction(transaction: TransactionsCreate, user=Depends(auth_handler.auth_wrapper)):
    db_transaction = Transaction(**transaction.dict())
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@main_router.put("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, transaction_data: TransactionsUpdate, user=Depends(auth_handler.auth_wrapper)):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction.category_id = transaction_data.category_id
    transaction.type = transaction_data.type
    transaction.value = transaction_data.value
    session.commit()
    return transaction

@main_router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, user=Depends(auth_handler.auth_wrapper)):
    transaction = session.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"message": "Transaction deleted"}

@main_router.post("/balances/{balance_id}/categories/", response_model=CategoryRead)
def create_category(balance_id: int, category: Category, user=Depends(auth_handler.auth_wrapper)):
    db_balance = session.get(Balance, balance_id)
    if not db_balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    new_category = Category(**category.dict(), balance_id=balance_id)
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category

@main_router.put("/categories/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, category_data: Category, user=Depends(auth_handler.auth_wrapper)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = category_data.name
    category.limit = category_data.limit
    session.commit()
    return category

@main_router.delete("/categories/{category_id}")
def delete_category(category_id: int, user=Depends(auth_handler.auth_wrapper)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"message": "Category deleted"}
```


#### Реализация авторизации и пользовательских эндпоинтов:

```
load_dotenv()

secret_key = os.getenv("JS_SECRET")


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
    secret = secret_key

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, user_id):
        if self.secret is None:
            raise ValueError("No SECRET_KEY set for JWT encoding")
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, self.secret, algorithm='HS256')

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Expired signature')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def get_current_user(self, auth: HTTPAuthorizationCredentials = Security(security)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
        username = self.decode_token(auth.credentials)
        if username is None:
            raise credentials_exception
        user = find_user(username)
        if username is None:
            raise credentials_exception
        return user
```


```
from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED

from auth import AuthHandler
from models import Balance, UserInput, User, UserLogin
from useful import select_all_users, find_user
from db import session

user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post('/registration', status_code=201, tags=['users'], description='Register new user')
def register(user: UserInput):
    users = select_all_users()
    if any(x.username == user.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_pwd = auth_handler.get_password_hash(user.password)
    balance = Balance(balance=0)
    u = User(username=user.username, password=hashed_pwd, balance=balance)
    session.add_all([u, balance])
    session.commit()

    return JSONResponse(status_code=201, content={"message": "User registered successfully"})


@user_router.post('/login', tags=['users'])
def login(user: UserLogin):
    user_found = find_user(user.username)

    if not user_found:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    verified = auth_handler.verify_password(user.password, user_found.password)

    if not verified:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')

    token = auth_handler.encode_token(user_found.username)
    return {'token': token}


@user_router.post('/users/me', tags=['users'])
def get_current_user(user: User = Depends(auth_handler.get_current_user)):
    return user.username
```

#### Другие файлы

```
from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DB_ADMIN")

engine = create_engine(db_url, echo=True)
session = Session(bind=engine)
```

```
from sqlmodel import select

from db import engine, Session
from models import User


def select_all_users():
    with Session(engine) as session:
        statement = select(User)
        res = session.exec(statement).all()
        return res


def find_user(name):
    with Session(engine) as session:
        statement = select(User).where(User.username == name)
        return session.exec(statement).first()
```

## Вывод

При выполнении данной лабораторной работы я изучил работу с FastAPI, научился работать с эндпоинтами.