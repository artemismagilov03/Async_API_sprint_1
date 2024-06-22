SELECT to_json(sub_query)
FROM (SELECT id   AS id,
             name AS name
      FROM genre
      -- WHERE fw.updated_at > NOW()
      ORDER BY name) AS sub_query;
