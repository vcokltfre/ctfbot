GET_UR = "SELECT u.id, u.discord_id, L.discord_role FROM ( SELECT User.id, User.discord_id, SUM(C.points) AS points FROM User LEFT JOIN ChallengeComplete CC ON User.id = CC.user LEFT JOIN Challenge C ON CC.challenge = C.id GROUP BY User.id ) u LEFT JOIN Level L ON L.points_required <= u.points"
GET_ROLES = "SELECT discord_role FROM Level;"
