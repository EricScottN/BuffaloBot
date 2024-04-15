CREATE TABLE IF NOT EXISTS public.region
(
    id serial NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT region_pk PRIMARY KEY (id)
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
