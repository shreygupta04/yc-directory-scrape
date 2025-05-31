import { pgTable, text, serial, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const scrapeJobs = pgTable("scrape_jobs", {
  id: serial("id").primaryKey(),
  batch: text("batch").notNull(),
  mode: text("mode").notNull().default("full"),
  status: text("status").notNull().default("pending"), // pending, running, completed, error
  progress: integer("progress").default(0),
  totalCompanies: integer("total_companies").default(0),
  processedCompanies: integer("processed_companies").default(0),
  errorCount: integer("error_count").default(0),
  errorMessage: text("error_message"),
  createdAt: timestamp("created_at").defaultNow(),
  completedAt: timestamp("completed_at"),
  options: jsonb("options"),
});

export const companies = pgTable("companies", {
  id: serial("id").primaryKey(),
  companyName: text("company_name").notNull(),
  batch: text("batch").notNull(),
  description: text("description"),
  website: text("website"),
  geo: text("geo"),
  founders: jsonb("founders"),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertScrapeJobSchema = createInsertSchema(scrapeJobs).pick({
  batch: true,
  mode: true,
  options: true,
});

export const insertCompanySchema = createInsertSchema(companies).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type InsertScrapeJob = z.infer<typeof insertScrapeJobSchema>;
export type ScrapeJob = typeof scrapeJobs.$inferSelect;
export type InsertCompany = z.infer<typeof insertCompanySchema>;
export type Company = typeof companies.$inferSelect;
