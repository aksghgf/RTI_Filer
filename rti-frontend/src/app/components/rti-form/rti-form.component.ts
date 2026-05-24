import { Component, ElementRef, inject, signal, viewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs/operators';
import { RtiResponse, RtiService } from '../../services/rti.service';

@Component({
  selector: 'app-rti-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rti-form.component.html',
  styleUrl: './rti-form.component.css'
})
export class RtiFormComponent {
  private readonly rtiService = inject(RtiService);
  private readonly resultPanel = viewChild<ElementRef<HTMLElement>>('resultPanel');

  userName = '';
  userLocation = '';
  problemText = '';

  loading = signal(false);
  loadingMessage = signal('Generating RTI...');
  errorMessage = signal('');
  result = signal<RtiResponse | null>(null);
  pdfUrl = signal('');
  pdfDownloadName = signal('RTI_Application.pdf');
  pdfDownloading = signal(false);

  onSubmit(): void {
    this.errorMessage.set('');
    this.result.set(null);
    this.pdfUrl.set('');
    this.pdfDownloadName.set('RTI_Application.pdf');

    const trimmedProblem = this.problemText.trim();
    if (trimmedProblem.length < 20) {
      this.errorMessage.set('Please describe your issue in at least 20 characters.');
      return;
    }

    if (!this.userName.trim() || !this.userLocation.trim()) {
      this.errorMessage.set('Name and location are required.');
      return;
    }

    this.loading.set(true);
    this.loadingMessage.set('Routing to ministry and drafting your RTI...');

    this.rtiService
      .generateRti({
        user_name: this.userName.trim(),
        user_location: this.userLocation.trim(),
        problem_text: trimmedProblem
      })
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (response) => {
          this.result.set(response);
          this.pdfUrl.set(this.rtiService.pdfDownloadUrl(response.pdf_path));
          this.pdfDownloadName.set(response.pdf_path.split(/[/\\]/).pop() || 'RTI_Application.pdf');
          this.scrollToResults();
        },
        error: (err) => {
          this.errorMessage.set(
            err?.error?.detail ||
              'Something went wrong while generating your RTI. Please try again.'
          );
        }
      });
  }

  downloadPdf(): void {
    const current = this.result();
    if (!current || this.pdfDownloading()) {
      return;
    }

    this.pdfDownloading.set(true);
    this.rtiService
      .downloadPdf(current.pdf_path)
      .pipe(finalize(() => this.pdfDownloading.set(false)))
      .subscribe({
        next: (blob) => {
          const objectUrl = URL.createObjectURL(blob);
          const anchor = document.createElement('a');
          anchor.href = objectUrl;
          anchor.download = this.pdfDownloadName();
          anchor.click();
          URL.revokeObjectURL(objectUrl);
        },
        error: () => {
          this.errorMessage.set('PDF download failed. Try opening the PDF link directly.');
        }
      });
  }

  private scrollToResults(): void {
    requestAnimationFrame(() => {
      this.resultPanel()?.nativeElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
}
