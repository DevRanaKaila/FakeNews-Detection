"""
Interactive Terminal Verification System
Allows real-time verification of raw news text, live news URLs, and batch file tests
with formatted diagnostic gauges, credibility meters, and author bias breakdowns.
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text

from src.live_pipeline import LiveVerificationPipeline
from src.models import HybridFakeNewsClassifier

console = Console()

def print_banner():
    banner_text = Text()
    banner_text.append("=" * 76 + "\n", style="bold cyan")
    banner_text.append("   AUTHENTICITY & AUTHOR BIAS NLP VERIFICATION SYSTEM\n", style="bold white on blue")
    banner_text.append("   Hybrid Stylometric, Sentiment & Stacking Transformer Pipeline\n", style="italic cyan")
    banner_text.append("   [Major Project: CSE & Allied Branches - Scopus Indexed Track]\n", style="dim yellow")
    banner_text.append("=" * 76, style="bold cyan")
    console.print(banner_text)

def render_verification_report(report: dict):
    console.print("\n" + "=" * 76, style="bold green")
    console.print("                     DETAILED VERIFICATION REPORT                     ", style="bold white on dark_green")
    console.print("=" * 76 + "\n", style="bold green")
    
    # 1. Headline & Source
    if report.get("title"):
        console.print(Panel(f"[bold]{report['title']}[/bold]", title="Article Headline", border_style="cyan"))
    if report.get("source_url"):
        console.print(f"[bold cyan]Source URL:[/bold cyan] {report['source_url']}")
        
    # 2. Verdict & Credibility Meter
    verdict = report["prediction_verdict"]
    score = report["credibility_score"]
    v_style = "bold green" if "REAL" in verdict else "bold red"
    
    table_verdict = Table(show_header=False, box=None)
    table_verdict.add_row("[bold]Classification Verdict:[/bold]", f"[{v_style}]{verdict}[/{v_style}]")
    table_verdict.add_row("[bold]Authenticity Credibility Score:[/bold]", f"[bold yellow]{score:.1f}%[/bold yellow] (0% = Definite Fake, 100% = Fully Authentic)")
    table_verdict.add_row("[bold]Fake Probability Index:[/bold]", f"[bold red]{report['fake_probability']*100:.2f}%[/bold red]")
    table_verdict.add_row("[bold]Authentic Probability Index:[/bold]", f"[bold green]{report['real_probability']*100:.2f}%[/bold green]")
    console.print(Panel(table_verdict, title="[bold]Authenticity Evaluation[/bold]", border_style="blue"))
    
    # 3. Author Tone & Biasness Profile (Mathematical Formulations)
    bias = report["author_bias"]
    table_bias = Table(title="Author Tone & Biasness Mathematical Breakdown", style="magenta")
    table_bias.add_column("Formulated Metric", style="cyan", justify="left")
    table_bias.add_column("Calculated Value", style="bold white", justify="center")
    table_bias.add_column("Interpretation / Qualitative Stance", style="italic yellow", justify="left")
    
    table_bias.add_row("Composite Author Bias Score (ABS)", f"{bias['author_bias_score']}/100", f"[{bias['bias_color']}]{bias['bias_level']}[/{bias['bias_color']}]")
    table_bias.add_row("Affective Tone / Sentiment", bias['tone_sentiment'], "Overall emotional valence")
    table_bias.add_row("Subjectivity Index (S_idx)", f"{bias['subjectivity_pct']}%", "Ratio of opinion adjectives vs facts")
    table_bias.add_row("Emotional Hyperbole Factor (EHF)", f"{bias['sensationalism_pct']}%", f"{bias['sensational_word_count']} Sensational / Exaggerated words")
    table_bias.add_row("Hedging & Uncertainty Ratio (HUR)", f"{bias['hedging_pct']}%", f"{bias['hedge_phrase_count']} Unverified Attribution terms")
    console.print(table_bias)
    
    # 4. Stylometric & Readability Profile
    read = report["readability"]
    table_read = Table(title="Linguistic Complexity & Surface Fingerprint", style="blue")
    table_read.add_column("Linguistic Metric", style="cyan")
    table_read.add_column("Calculated Index", style="bold white")
    table_read.add_column("Standard Reading Grade", style="yellow")
    
    table_read.add_row("Flesch Reading Ease (FRE)", str(read["flesch_reading_ease"]), "Higher = Standard Public / Lower = Dense")
    table_read.add_row("Flesch-Kincaid Grade Level", f"Grade {read['fkgl_grade_level']}", "Equivalent US Schooling Grade")
    table_read.add_row("Gunning Fog Index (GFI)", str(read["gunning_fog"]), "Years of Formal Education to Understand")
    table_read.add_row("Lexical Diversity (Type-Token Ratio)", str(read["lexical_diversity_ttr"]), "Vocabulary Richness Index")
    console.print(table_read)
    
    # 5. Sentence-Level Explainability Highlights
    flagged = report.get("flagged_deceptive_sentences", [])
    if flagged:
        console.print("\n[bold red][!] Suspicious / Hyperbolic Passages Flagged for Review:[/bold red]")
        for item in flagged:
            reasons_str = ", ".join(item["reasons"])
            console.print(f"  [bold yellow]• Sentence #{item['sentence_idx']}:[/bold yellow] "{item['sentence_text']}"")
            console.print(f"    [dim red]→ Reasons: {reasons_str} (Deception Risk: {item['risk_score']})[/dim red]")
    else:
        console.print("\n[bold green][✓] No high-risk deceptive linguistic passages detected.[/bold green]")
    console.print("\n" + "=" * 76 + "\n", style="bold green")

def main():
    print_banner()
    
    # Initialize Pipeline
    model_path = os.path.join("data", "processed", "best_hybrid_model.joblib")
    if os.path.exists(model_path):
        console.print(f"[bold green]✓ Loading Pre-Trained Hybrid Stacking Model from {model_path}...[/bold green]")
        pipeline = LiveVerificationPipeline(model_path=model_path)
    else:
        console.print("[yellow]! Model checkpoint not found. Training quick baseline on benchmark corpus...[/yellow]")
        from src.utils import generate_benchmark_dataset
        df = generate_benchmark_dataset(num_samples=300)
        clf = HybridFakeNewsClassifier(model_type="hybrid_stacking")
        clf.train(df['text'].tolist(), df['label'].tolist(), titles=df['title'].tolist())
        pipeline = LiveVerificationPipeline()
        pipeline.set_model(clf)
        console.print("[green]✓ Baseline model initialized successfully.[/green]")
        
    while True:
        console.print("\n[bold cyan]Select Verification Mode:[/bold cyan]")
        console.print("  [bold white][1][/bold white] Verify Live News Web URL (Real-time Scraping & Parsing)")
        console.print("  [bold white][2][/bold white] Verify Custom News Text / Headline (Interactive Paste)")
        console.print("  [bold white][3][/bold white] Run Live Built-in Diagnostic Demo (Real vs Fake Samples)")
        console.print("  [bold white][4][/bold white] Exit Application")
        
        choice = Prompt.ask("\nEnter choice", choices=["1", "2", "3", "4"], default="3")
        
        if choice == "1":
            url = Prompt.ask("\n[bold yellow]Enter live news article URL[/bold yellow]")
            with console.status("[bold green]Scraping and analyzing live web content...[/bold green]"):
                parsed = pipeline.fetch_article_from_url(url)
            if parsed.get("error"):
                console.print(f"[bold red]Error scraping URL:[/bold red] {parsed['error']}")
                continue
            report = pipeline.verify_news(parsed["text"], title=parsed["title"], source_url=url)
            render_verification_report(report)
            
        elif choice == "2":
            title = Prompt.ask("\n[bold yellow]Enter Article Title / Headline[/bold yellow]")
            text = Prompt.ask("[bold yellow]Enter Full Article Body Content[/bold yellow]")
            if not text.strip():
                console.print("[red]Article body cannot be empty![/red]")
                continue
            with console.status("[bold green]Computing stylometrics, author bias & authenticity...[/bold green]"):
                report = pipeline.verify_news(text, title=title)
            render_verification_report(report)
            
        elif choice == "3":
            console.print("\n[bold cyan]Select Built-In Sample Test:[/bold cyan]")
            console.print("  [1] Real Scientific Article (NASA James Webb Telescope)")
            console.print("  [2] Sensational Fake / Misinformation Article (Secret Vaults & Aliens)")
            sub_choice = Prompt.ask("Choose sample", choices=["1", "2"], default="1")
            
            if sub_choice == "1":
                title = "NASA James Webb Space Telescope Discovers Distant Galaxy Cluster"
                text = "Astronomers utilizing the James Webb Space Telescope have identified a high-redshift galaxy cluster dating back 13 billion years. The spectroscopic data confirmed standard cosmological models with unprecedented resolution and minimal optical distortion. Peer-reviewed findings were published in the Astrophysical Journal following rigorous multi-institution validation."
            else:
                title = "SHOCKING: Secret Government Underground Base Exposed by Whistleblower!"
                text = "You won't believe what insiders are secretly claiming! A bombshell report reveals that elite conspirators have allegedly hidden alien technology in subterranean vaults. Mainstream media is totally terrified to report this insane truth! Sources claim disaster is imminent and corrupt politicians are panicking!"
                
            with console.status("[bold green]Executing comprehensive analysis...[/bold green]"):
                report = pipeline.verify_news(text, title=title)
            render_verification_report(report)
            
        elif choice == "4":
            console.print("\n[bold green]Exiting Authenticity Verification System. Thank you![/bold green]\n")
            sys.exit(0)

if __name__ == "__main__":
    main()
