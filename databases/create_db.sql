CREATE TABLE users
(
    id          INTEGER PRIMARY KEY,
    is_admin    BOOLEAN     NOT NULL
                         DEFAULT FALSE,
    is_active   BOOLEAN     NOT NULL
                         DEFAULT FALSE,
    last_active DATETIME DEFAULT (datetime('now', 'localtime')),
    username    VARCHAR(30) NOT NULL UNIQUE,
    password    VARCHAR(30) NOT NULL UNIQUE
);


CREATE TABLE categories
(
    codename VARCHAR(255) PRIMARY KEY,
    name     VARCHAR(255)
);

CREATE TABLE expense
(
    id                INTEGER,
    amount            REAL,
    created           DATETIME,
    category_codename VARCHAR(255),
    FOREIGN KEY (
                 category_codename
        )
        REFERENCES categories (codename),
    FOREIGN KEY (
                 id
        )
        REFERENCES users (id)
);

INSERT INTO categories (codename,
                        name)
VALUES ("products",
        "🛒 продукты"),
       ("coffee",
        "☕️кофе"),
       ("dinner",
        "🍽️ обед"),
       ("cafe",
        "🍔 кафе"),
       ("transport",
        "🚌 общ. транспорт"),
       ("taxi",
        "🚕 такси"),
       ("phone",
        "☎️телефон"),
       ("books",
        "📚 книги"),
       ("internet",
        "📡 интернет"),
       ("subscriptions",
        "✅ подписки"),
       ("other",
        "прочее");
