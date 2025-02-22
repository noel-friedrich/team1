import mongoose from "mongoose";

const MONGODB_URI = process.env.MONGODB_URI || "";

if (!MONGODB_URI) {
  throw new Error("Please define the MONGODB_URI environment variable");
}

export const connectToDatabase = async () => {
  try {
    // Force close any existing connection
    if (mongoose.connection.readyState !== 0) {
      await mongoose.connection.close();
    }

    // Log the URI we're using (with password redacted)
    const redactedUri = MONGODB_URI.replace(/:([^@]+)@/, ':****@');
    console.log('Connecting to MongoDB with URI:', redactedUri);

    // Connect with explicit database selection
    await mongoose.connect(MONGODB_URI, {
      dbName: 'william'  // Explicitly set database name
    });

    const db = mongoose.connection.db;
    if (!db) {
      throw new Error('Database connection not established');
    }

    console.log('Connected to database:', db.databaseName);
    
    // List all collections
    const collections = await db.collections();
    console.log('Available collections:', collections.map(c => c.collectionName));

  } catch (error) {
    console.error('MongoDB connection error:', error);
    throw error;
  }
};
