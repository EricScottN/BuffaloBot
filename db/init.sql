BEGIN;

CREATE SEQUENCE region_id_seq;

CREATE TABLE IF NOT EXISTS public.region
(
    id integer NOT NULL DEFAULT nextval('region_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT region_pk PRIMARY KEY (id)
);

CREATE SEQUENCE role_group_id_seq;

CREATE TABLE IF NOT EXISTS public.role_group
(
    id integer NOT NULL DEFAULT nextval('role_group_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default" NOT NULL,
    permission_value bigint NOT NULL,
    CONSTRAINT role_group_pk PRIMARY KEY (id),
    CONSTRAINT name_permissions_key UNIQUE (name, permission_value)
);

INSERT INTO public.region (name)
VALUES
    ('Amherst'),
    ('Aurora'),
    ('Buffalo'),
    ('Cheektowaga'),
    ('Clarence'),
    ('Eden'),
    ('Evans'),
    ('Grand Island'),
    ('Hamburg'),
    ('Lackawanna'),
    ('Lancaster'),
    ('Niagara Falls'),
    ('Orchard Park'),
    ('Tonawanda'),
    ('West Seneca'),
    ('North Tonawanda'),
    ('Lockport'),
    ('Just Visiting'),
    ('Nearby');

INSERT INTO public.role_group (name, permission_value)
VALUES
    ('region', 281357436993),
    ('elevated', 18552215423553),
    ('mod', 28448907062215),
    ('admin', 422212465065975);

COMMIT;