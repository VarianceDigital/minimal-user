--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5 (Ubuntu 14.5-1.pgdg20.04+1)
-- Dumped by pg_dump version 14.3

-- Started on 2022-10-27 13:41:30 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA minimaluser;


CREATE TABLE minimaluser.tbl_auth (
    aut_id bigint NOT NULL,
    aut_email character varying(255) NOT NULL,
    aut_key character varying(128) NOT NULL,
    aut_name character varying(100),
    aut_isvalid boolean DEFAULT true NOT NULL,
    aut_confirmed boolean DEFAULT false,
    aut_timestamp timestamp with time zone DEFAULT now(),
    aut_otp character varying(10),
    aut_key_temp character varying(128),
    aut_tile character varying(50)
);


ALTER TABLE minimaluser.tbl_auth ALTER COLUMN aut_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME minimaluser.tbl_auth_aut_id_seq
    START WITH 10
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


CREATE TABLE minimaluser.tbl_image (
    img_id bigint NOT NULL,
    img_name character varying(124),
    img_caption character varying(255),
    img_filename character varying(255) NOT NULL,
    img_tstamp timestamp with time zone DEFAULT now() NOT NULL,
    img_onair boolean DEFAULT true NOT NULL,
    img_seqno integer DEFAULT 0,
    img_is_in_hp boolean DEFAULT false
);


INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (8, 'You are late!', 'We are hungry.', 'kitchen2.jpg', '2022-08-26 09:29:23.832889+00', true, 8, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (1, 'Apple-Cat', 'Tau loves laptops.', 'applecat.jpg', '2022-08-25 12:14:15.421157+00', true, 1, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (2, 'White as snow', 'Pi''s paws are soft!', 'beauty.jpg', '2022-08-25 12:15:23.859847+00', true, 2, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (3, 'I''m invisible', 'Most of the time...', 'coocoo.jpg', '2022-08-25 15:18:54.200687+00', true, 3, true);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (4, 'Perfect symmetry', 'But unstable equilibrium.', 'gattonzisimmetrici.jpg', '2022-08-25 15:20:43.265025+00', true, 4, true);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (5, 'Urban forest ', 'Dominating the street.', 'green.jpg', '2022-08-25 15:22:22.81356+00', true, 5, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (6, 'Pink nose', 'Am I cute?', 'imcute.jpg', '2022-08-26 09:24:58.203425+00', true, 6, true);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (9, 'Like a pro', 'Tau tries to teach how to lay down.', 'likeapro.jpg', '2022-08-26 09:31:26.428694+00', true, 9, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (10, 'Like a pro v.2', 'Tau tries to teach how to lay down. Again.', 'likeapro2.jpg', '2022-08-26 09:32:42.679881+00', true, 10, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (15, 'Brother and sister', 'One cushion each.', 'twoinbed.jpg', '2022-08-26 09:40:40.375683+00', true, 13, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (16, 'Soft sun', 'Let''s peek outside.', 'twoinbed2.jpg', '2022-08-26 09:42:35.190133+00', true, 14, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (17, 'I need cuddles', 'What are you waiting for?', 'whatareyouwaitingfor.jpg', '2022-08-26 09:43:34.034881+00', true, 15, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (11, 'Spider', 'The new friend stopped playing after a while.', 'spider.jpg', '2022-08-26 09:34:02.181243+00', true, 11, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (14, 'Hmmm...', 'Pi thinks humans are strange bipeds.', 'spunta.jpg', '2022-08-26 09:34:02.181243+00', true, 12, false);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (18, 'I''m special', 'So you want to be a cat?...', 'whatsup.jpg', '2022-08-26 09:45:24.599242+00', true, 16, true);
INSERT INTO minimaluser.tbl_image OVERRIDING SYSTEM VALUE VALUES (7, 'Sous-chef', 'Waiting for the human cook.', 'kitchen1.jpg', '2022-08-26 09:27:15.86196+00', true, 7, false);



ALTER TABLE ONLY minimaluser.tbl_auth
    ADD CONSTRAINT tbl_auth_pkey PRIMARY KEY (aut_id);



ALTER TABLE ONLY minimaluser.tbl_image
    ADD CONSTRAINT tbl_image_pkey PRIMARY KEY (img_id);