GET_UR = "SELECT u.id, u.discord_id, L.discord_role FROM ( SELECT User.id, User.discord_id, SUM(C.points) AS points FROM User LEFT JOIN ChallengeComplete CC ON User.id = CC.user LEFT JOIN Challenge C ON CC.challenge = C.id GROUP BY User.id ) u LEFT JOIN Level L ON L.points_required <= u.points"
GET_ROLES = "SELECT discord_role FROM Level;"
LEADERBOARD = "SELECT User.discord_id, ( SELECT COALESCE(SUM(C.points), 0) FROM ChallengeComplete CC INNER JOIN Challenge C ON C.id = CC.challenge WHERE CC.user = User.id ) points FROM User ORDER BY points DESC, (SELECT MAX(CC.created_at) FROM ChallengeComplete CC WHERE CC.user = User.id) ASC, User.created_at ASC"

COMPLETED = """SELECT CC.created_at, U.discord_id, A.name AS category, C.name AS challenge, C.points
FROM ChallengeComplete CC
INNER JOIN User U ON U.id = CC.user
INNER JOIN Challenge C ON C.id = CC.challenge
INNER JOIN Category A ON A.id = C.category
WHERE U.discord_id = %s
ORDER BY CC.created_at DESC"""