import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RtiRequest {
  user_name: string;
  user_location: string;
  problem_text: string;
}

export interface RtiResponse {
  status: string;
  detected_ministry: string;
  pdf_path: string;
  draft_preview: string;
}

@Injectable({
  providedIn: 'root'
})
export class RtiService {
  private readonly apiUrl = environment.apiUrl;
  private readonly http = inject(HttpClient);

  generateRti(payload: RtiRequest): Observable<RtiResponse> {
    return this.http.post<RtiResponse>(`${this.apiUrl}/api/v1/generate-rti`, payload);
  }

  pdfDownloadUrl(pdfPath: string): string {
    const normalized = pdfPath.replace(/\\/g, '/');
    const withSlash = normalized.startsWith('/') ? normalized : `/${normalized}`;
    return `${this.apiUrl}${withSlash}`;
  }

  downloadPdf(pdfPath: string): Observable<Blob> {
    return this.http.get(this.pdfDownloadUrl(pdfPath), { responseType: 'blob' });
  }
}
