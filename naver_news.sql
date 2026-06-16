drop table naver_news;
create table naver_news (
    id int primary key auto_increment,
    title varchar(512),
    originallink varchar(512),
    link varchar(512),
    description text,
    pub_date varchar(512),
    created_at datetime default (current_timestamp)
);

alter table naver_news
add constraint uq_naver_news_link unique (link);