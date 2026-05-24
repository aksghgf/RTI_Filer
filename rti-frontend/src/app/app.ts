import { Component } from '@angular/core';
import { RtiFormComponent } from './components/rti-form/rti-form.component';

@Component({
  selector: 'app-root',
  imports: [RtiFormComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  title = 'RTI Auto-Filer';
}
