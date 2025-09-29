// MongoDB initialization script
db = db.getSiblingDB('tennis_tracking');

// Create collections
db.createCollection('users');
db.createCollection('matches');
db.createCollection('videos');
db.createCollection('analysis_tasks');
db.createCollection('player_stats');
db.createCollection('game_events');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.matches.createIndex({ "date": -1 });
db.matches.createIndex({ "player1.id": 1, "player2.id": 1 });
db.videos.createIndex({ "uploadedAt": -1 });
db.videos.createIndex({ "userId": 1 });
db.analysis_tasks.createIndex({ "status": 1, "createdAt": -1 });
db.player_stats.createIndex({ "playerId": 1, "matchId": 1 });
db.game_events.createIndex({ "matchId": 1, "timestamp": 1 });

// Insert default admin user (password: admin123 - hashed with bcrypt)
db.users.insertOne({
    _id: ObjectId(),
    username: "admin",
    email: "admin@tennis-tracking.com",
    fullName: "System Administrator",
    password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY3JeJLpN0HzYe.",
    role: "admin",
    isActive: true,
    createdAt: new Date(),
    updatedAt: new Date()
});

// Insert sample data
db.matches.insertOne({
    _id: ObjectId(),
    matchId: "match_001",
    player1: {
        id: "player_001",
        name: "Roger Federer",
        country: "Switzerland",
        ranking: 10
    },
    player2: {
        id: "player_002",
        name: "Rafael Nadal",
        country: "Spain",
        ranking: 4
    },
    tournament: "ATP Masters",
    round: "Final",
    surface: "hard",
    date: new Date("2024-09-28"),
    score: {
        sets: [
            { player1Games: 6, player2Games: 4 },
            { player1Games: 6, player2Games: 2 }
        ],
        winner: "player1"
    },
    duration: 135, // minutes
    location: "Miami, USA",
    status: "completed",
    statistics: {
        player1: {
            aces: 12,
            doubleFaults: 2,
            firstServePercentage: 68,
            winningShots: 35,
            unforcedErrors: 18
        },
        player2: {
            aces: 8,
            doubleFaults: 3,
            firstServePercentage: 62,
            winningShots: 28,
            unforcedErrors: 22
        }
    },
    createdAt: new Date(),
    updatedAt: new Date()
});

print('MongoDB initialization completed successfully!');
print('Default admin user created - username: admin, password: admin123');