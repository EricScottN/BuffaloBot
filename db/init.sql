BEGIN;

CREATE TABLE IF NOT EXISTS public.region
(
    id serial NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT region_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.role_group
(
    id serial NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    permission_value bigint NOT NULL,
    CONSTRAINT role_group_pk PRIMARY KEY (id),
    CONSTRAINT role_group_name_key UNIQUE (name)
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