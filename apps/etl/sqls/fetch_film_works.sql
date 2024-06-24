SELECT to_json(sub_query)
FROM (SELECT fw.id                                     AS id,
             fw.rating                                 AS rating,
             COALESCE(json_agg(DISTINCT g.name), '[]') AS genres,
             fw.title                                  AS title,
             fw.description                            AS description,
             ARRAY_TO_STRING(
                     COALESCE(
                                     array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director'),
                                     '{}'
                     ), ',')                           AS directors_names,
             ARRAY_TO_STRING(
                     COALESCE(
                                     array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor'),
                                     '{}'), ',')       AS actors_names,
             ARRAY_TO_STRING(
                     COALESCE(
                                     array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer'),
                                     '{}'), ',')       AS writers_names,
             COALESCE(
                             json_agg(
                             DISTINCT jsonb_build_object(
                                     'id', p.id,
                                     'name', p.full_name
                                      )
                                     ) FILTER (WHERE pfw.role = 'director'),
                             '[]'
             )                                         AS directors,
             COALESCE(
                             json_agg(
                             DISTINCT jsonb_build_object(
                                     'id', p.id,
                                     'name', p.full_name
                                      )
                                     ) FILTER (WHERE pfw.role = 'actor'),
                             '[]'
             )                                         AS actors,
             COALESCE(
                             json_agg(
                             DISTINCT jsonb_build_object(
                                     'id', p.id,
                                     'name', p.full_name
                                      )
                                     ) FILTER (WHERE pfw.role = 'writer'),
                             '[]'
             )                                         AS writers
      FROM film_work fw
               LEFT JOIN person_film_work pfw
                         ON pfw.film_work_id = fw.id
               LEFT JOIN person p ON p.id = pfw.person_id
               LEFT JOIN genre_film_work gfw ON gfw.film_work_id = fw.id
               LEFT JOIN genre g ON g.id = gfw.genre_id
      -- WHERE fw.updated_at > NOW()
      GROUP BY fw.id
      ORDER BY fw.updated_at
      LIMIT NULL) AS sub_query;
