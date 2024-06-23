SELECT to_json(sub_query)
FROM (SELECT p.id        AS id,
             p.full_name AS full_name,
             json_agg(DISTINCT jsonb_build_object(
                     'id', pfw.id,
                     'roles', pfw.roles)
             )           AS films

      FROM person AS p
               INNER JOIN (SELECT id, person_film_work.person_id, array_agg(DISTINCT role) AS roles
                           FROM person_film_work
                           GROUP BY person_film_work.id) AS pfw ON p.id = pfw.person_id
      GROUP BY p.id
      ORDER BY p.id) AS sub_query;
