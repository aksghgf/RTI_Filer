import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RtiResponse, RtiService } from '../../services/rti.service';

@Component({
  selector: 'app-rti-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rti-form.component.html',
  styleUrl: './rti-form.component.css'
})
export class RtiFormComponent {
  userName = '';
  userLocation = '';
  problemText = '';

  loading = false;
  errorMessage = '';
  result: RtiResponse | null = null;
  pdfUrl = '';

  constructor(private rtiService: RtiService) {}

  onSubmit(): void {
    this.errorMessage = '';
    this.result = null;
    this.pdfUrl = '';

    const trimmedProblem = this.problemText.trim();
    if (trimmedProblem.length < 20) {
      this.errorMessage = 'Please describe your issue in at least 20 characters.';
      return;
    }

    if (!this.userName.trim() || !this.userLocation.trim()) {
      this.errorMessage = 'Name and location are required.';
      return;
    }

    this.loading = true;

    this.rtiService
      .generateRti({
        user_name: this.userName.trim(),
        user_location: this.userLocation.trim(),
        problem_text: trimmedProblem
      })
      .subscribe({
        next: (response) => {
          this.result = response;
          this.pdfUrl = this.rtiService.pdfDownloadUrl(response.pdf_path);
          this.loading = false;
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage =
            err?.error?.detail ||
            'Something went wrong while generating your RTI. Please try again.';
        }
      });
  }
}
