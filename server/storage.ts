import { users, scrapeJobs, companies, type User, type InsertUser, type ScrapeJob, type InsertScrapeJob, type Company, type InsertCompany } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  createScrapeJob(job: InsertScrapeJob): Promise<ScrapeJob>;
  getScrapeJob(id: number): Promise<ScrapeJob | undefined>;
  getAllScrapeJobs(): Promise<ScrapeJob[]>;
  updateScrapeJob(id: number, updates: Partial<ScrapeJob>): Promise<ScrapeJob | undefined>;
  
  createCompany(company: InsertCompany): Promise<Company>;
  getCompaniesByBatch(batch: string): Promise<Company[]>;
  getAllCompanies(): Promise<Company[]>;
  getCompanyStats(): Promise<{
    totalCompanies: number;
    activeBatches: number;
    lastUpdate: Date | null;
    successRate: number;
  }>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private scrapeJobs: Map<number, ScrapeJob>;
  private companies: Map<number, Company>;
  private currentUserId: number;
  private currentJobId: number;
  private currentCompanyId: number;

  constructor() {
    this.users = new Map();
    this.scrapeJobs = new Map();
    this.companies = new Map();
    this.currentUserId = 1;
    this.currentJobId = 1;
    this.currentCompanyId = 1;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createScrapeJob(insertJob: InsertScrapeJob): Promise<ScrapeJob> {
    const id = this.currentJobId++;
    const job: ScrapeJob = {
      ...insertJob,
      id,
      status: "pending",
      progress: 0,
      totalCompanies: 0,
      processedCompanies: 0,
      errorCount: 0,
      errorMessage: null,
      createdAt: new Date(),
      completedAt: null,
    };
    this.scrapeJobs.set(id, job);
    return job;
  }

  async getScrapeJob(id: number): Promise<ScrapeJob | undefined> {
    return this.scrapeJobs.get(id);
  }

  async getAllScrapeJobs(): Promise<ScrapeJob[]> {
    return Array.from(this.scrapeJobs.values()).sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  async updateScrapeJob(id: number, updates: Partial<ScrapeJob>): Promise<ScrapeJob | undefined> {
    const job = this.scrapeJobs.get(id);
    if (!job) return undefined;
    
    const updatedJob = { ...job, ...updates };
    this.scrapeJobs.set(id, updatedJob);
    return updatedJob;
  }

  async createCompany(insertCompany: InsertCompany): Promise<Company> {
    const id = this.currentCompanyId++;
    const company: Company = {
      ...insertCompany,
      id,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.companies.set(id, company);
    return company;
  }

  async getCompaniesByBatch(batch: string): Promise<Company[]> {
    return Array.from(this.companies.values()).filter(
      (company) => company.batch === batch
    );
  }

  async getAllCompanies(): Promise<Company[]> {
    return Array.from(this.companies.values());
  }

  async getCompanyStats(): Promise<{
    totalCompanies: number;
    activeBatches: number;
    lastUpdate: Date | null;
    successRate: number;
  }> {
    const companies = Array.from(this.companies.values());
    const jobs = Array.from(this.scrapeJobs.values());
    
    const totalCompanies = companies.length;
    const activeBatches = new Set(companies.map(c => c.batch)).size;
    const lastUpdate = companies.length > 0 
      ? companies.reduce((latest, company) => 
          company.updatedAt > latest ? company.updatedAt : latest, companies[0].updatedAt)
      : null;
    
    const completedJobs = jobs.filter(j => j.status === 'completed').length;
    const totalJobs = jobs.length;
    const successRate = totalJobs > 0 ? (completedJobs / totalJobs) * 100 : 100;

    return {
      totalCompanies,
      activeBatches,
      lastUpdate,
      successRate: Math.round(successRate * 10) / 10,
    };
  }
}

export const storage = new MemStorage();
