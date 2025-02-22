import mongoose, { Schema, Document, CallbackError } from "mongoose";

export interface IArticle extends Document {
  title: string;
  slug: string;
  content: string;
  image_url: string;
  createdAt: Date;
  votes: number;
}

const ArticleSchema: Schema<IArticle> = new Schema({
  title: { type: String, required: true },
  slug: { type: String, required: true, unique: true },
  content: { type: String, required: true },
  image_url: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
  votes: { type: Number, default: 0 },
});

// Fix: Correct TypeScript typing for the pre-save middleware
ArticleSchema.pre<IArticle>("save", function (next: (err?: CallbackError) => void) {
  if (this.isModified("title")) {
    this.slug = this.title.toLowerCase().replace(/\s+/g, "-");
  }
  next();
});

export default mongoose.models.Article || mongoose.model<IArticle>("Article", ArticleSchema);
