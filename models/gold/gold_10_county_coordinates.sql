MODEL (
  name gold.county_coordinates,
  kind FULL,
  description 'Gold 10: County centroid coordinates for map visualizations'
);

SELECT county, latitude, longitude
FROM (
  VALUES
    ('Davidson',   36.1627, -86.7816),
    ('Williamson', 35.9201, -86.8897),
    ('Rutherford', 35.8456, -86.4169),
    ('Montgomery', 36.4995, -87.3594),
    ('Wilson',     36.2334, -86.3002),
    ('Sumner',     36.4673, -86.4614),
    ('Maury',      35.6145, -87.0536),
    ('Putnam',     36.1395, -85.4977),
    ('Dickson',    36.0770, -87.3692),
    ('Robertson',  36.5270, -86.8697),
    ('Bedford',    35.5145, -86.4580),
    ('Coffee',     35.4837, -86.0603)
) AS t(county, latitude, longitude)
