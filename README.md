# Promptlane

A collaborative platform for managing, versioning, and sharing AI prompts.

![Promptlane Screenshot](docs/images/screenshot.png)

## Features

- **Organize** prompts into projects
- **Version** prompt templates
- **Collaborate** with team members
- **Track** prompt usage and changes
- **API** for integration with your applications

## Quick Start

### Prerequisites

- Python 3.8+
- FastAPI
- SQLAlchemy

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/promptlane.git
   cd promptlane
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open your browser and navigate to http://localhost:8000

## Documentation

For detailed documentation, see the [docs folder](docs/README.md).

## Email Templates

Promptlane uses a template-based email system for all outgoing emails. The templates are located in `app/templates/email/` and use Jinja2 for rendering.

### Template Structure

- **base.html**: Base template with common styling and layout
- **invitation.html**: Template for user invitation emails
- **password_reset.html**: Template for password reset emails
- **notification.html**: Template for general notifications

For detailed documentation on the email template system, see [Email Templates Documentation](docs/email_templates.md).

### Customizing Templates

To customize email templates:

1. Edit the template files in `app/templates/email/`
2. Templates use Jinja2 templating language with blocks for different sections
3. The base template includes common styling that can be extended

### Environment Configuration

Email configuration is managed through environment variables:

```
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=noreply@promptlane.example.com
EMAIL_PASSWORD=your-secure-password
EMAIL_FROM=Promptlane <noreply@promptlane.example.com>
SITE_URL=https://promptlane.example.com
```

## API Reference

The API documentation is available at http://localhost:8000/docs once the application is running.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
This project is licensed under the MIT License. 