CREATE TABLE IF NOT EXISTS public.regions
(
    id serial NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT regions_pk PRIMARY KEY (id)
);

INSERT INTO public.regions (name)
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
