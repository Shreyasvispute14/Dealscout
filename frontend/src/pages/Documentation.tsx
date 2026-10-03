import { Link } from "react-router-dom";
import { ArrowLeft, BookOpen, CheckCircle2, Download, FileText, GraduationCap, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { downloadProjectReport } from "@/lib/report";

const sections = [
  ["01", "Introduction", "Problem statement, motivation, objectives, and scope of the SPPU TYBSc CS project."],
  ["02", "Existing & Proposed System", "Manual price checking is slow. DealScout collects normalized offers and recommends the lowest suitable deal."],
  ["03", "Requirements", "HTML5, CSS3, JavaScript concepts, Python REST API concepts, MongoDB used as the project data store, and a modern browser."],
  ["04", "System Design", "Modules include login, product search, demo/live provider adapter, comparison engine, best-deal logic, and collected-data view."],
  ["05", "Implementation", "Product data is normalized into one offer structure so every seller can be compared using the same fields."],
  ["06", "Testing & Results", "Search validation, login validation, best-price selection, live fallback, and data collection are verified through the app flow."],
  ["07", "Conclusion & Future Scope", "Provider keys, more categories, location-aware delivery, and a relational SQLite deployment can be added later."],
];

export default function Documentation() {
  return (
    <main className="min-h-svh bg-[#f8fafc] px-4 py-8 text-[#0f172a] sm:px-8">
      <div className="mx-auto max-w-6xl">
        <Link to="/" className="mb-8 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-slate-950" data-testid="docs-back-link">
          <ArrowLeft className="size-4" /> Back to comparison
        </Link>
        <section className="mb-10 grid gap-8 lg:grid-cols-[1.25fr_.75fr] lg:items-end">
          <div>
            <p className="mb-4 font-mono text-xs uppercase tracking-[0.2em] text-emerald-700" data-testid="docs-eyebrow">Academic documentation</p>
            <h1 className="max-w-3xl font-heading text-4xl font-black tracking-tight sm:text-6xl" data-testid="docs-page-title">Your project report, organized for evaluation.</h1>
            <p className="mt-5 max-w-2xl text-lg leading-relaxed text-slate-600" data-testid="docs-page-description">A starter index, SPPU syllabus mapping, certificate templates, and software requirements. Replace the placeholder college details with your department guidelines.</p>
          </div>
          <Card className="border-slate-200 bg-white shadow-sm" data-testid="docs-project-card">
            <CardContent className="p-6">
              <div className="mb-4 flex items-center justify-between"><Badge className="bg-emerald-100 text-emerald-800">TYBSc CS • SPPU</Badge><GraduationCap className="size-5 text-emerald-600" /></div>
              <p className="font-heading text-xl font-bold">DealScout</p>
              <p className="mt-2 text-sm text-slate-500">E-commerce product comparison and best-deal recommendation system</p>
              <Button onClick={downloadProjectReport} className="mt-5 w-full bg-[#0f172a] text-white hover:bg-slate-800" data-testid="download-project-report-button"><Download className="size-4" /> Download project report</Button>
              <p className="mt-2 text-xs leading-relaxed text-slate-400" data-testid="report-download-note">Word-compatible .doc file using Times New Roman, exact chapter order, title page, certificate, index, and diagram placeholders.</p>
            </CardContent>
          </Card>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <Card className="border-slate-200 bg-white" data-testid="docs-index-card">
            <CardHeader className="border-b border-slate-100"><CardTitle className="flex items-center gap-2"><BookOpen className="size-5 text-emerald-600" /> Project index</CardTitle></CardHeader>
            <CardContent className="p-6"><ol className="space-y-4">{sections.map(([number, title, description]) => <li key={number} className="flex gap-4" data-testid={`docs-index-item-${number}`}><span className="font-mono text-xs text-emerald-700">{number}</span><div><p className="font-semibold">{title}</p><p className="mt-1 text-sm leading-relaxed text-slate-500">{description}</p></div></li>)}</ol></CardContent>
          </Card>

          <div className="space-y-6">
            <Card className="border-slate-200 bg-white" data-testid="docs-requirements-card">
              <CardHeader className="border-b border-slate-100"><CardTitle className="flex items-center gap-2"><CheckCircle2 className="size-5 text-emerald-600" /> Requirements checklist</CardTitle></CardHeader>
              <CardContent className="grid gap-4 p-6 sm:grid-cols-2">{["Modern browser", "Python 3.11+", "FastAPI REST concepts", "MongoDB / SQLite concepts", "HTML, CSS, JavaScript concepts", "Internet for optional live provider"].map((item) => <div key={item} className="flex items-start gap-2 text-sm text-slate-600" data-testid={`docs-requirement-${item.toLowerCase().replaceAll(" ", "-")}`}><span className="mt-1 size-2 rounded-full bg-emerald-500" />{item}</div>)}</CardContent>
            </Card>
            <Card className="border-slate-200 bg-[#0f172a] text-white" data-testid="docs-certificate-card">
              <CardHeader><CardTitle className="flex items-center gap-2"><FileText className="size-5 text-emerald-400" /> Certificate & declaration templates</CardTitle></CardHeader>
              <CardContent className="space-y-4 p-6 text-sm leading-relaxed text-slate-300"><p>“This is to certify that __________________ has completed the project DealScout under the guidance of __________________ during the academic year __________.”</p><p>Declaration: “I declare that this project is my original work prepared for the TYBSc Computer Science course.”</p><div className="flex items-center gap-2 border-t border-white/10 pt-4 text-emerald-300"><ShieldCheck className="size-4" /> Add signatures, seal, guide, and principal details as per your college format.</div></CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}