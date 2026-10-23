using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Options;

namespace MusicEventManagementSystem.API.Services.Marketing
{
    public interface IEmailSender
    {
        Task SendAsync(string to, string subject, string body, string? replyTo, string? replyToName, CancellationToken ct = default);
    }

    /// <summary>Sends plain-text e-mails. In "pickup" mode each message is written as an .eml file
    /// (open it with any mail client); in "smtp" mode it goes to an SMTP server such as Mailpit.</summary>
    public class EmailSender : IEmailSender
    {
        private readonly EmailOptions _opt;
        private readonly string _pickupDir;

        public EmailSender(IOptions<EmailOptions> opt, IWebHostEnvironment env)
        {
            _opt = opt.Value;
            _pickupDir = Path.IsPathRooted(_opt.PickupDirectory)
                ? _opt.PickupDirectory
                : Path.Combine(env.ContentRootPath, _opt.PickupDirectory);
        }

        public async Task SendAsync(string to, string subject, string body, string? replyTo, string? replyToName,
                                    CancellationToken ct = default)
        {
            using var msg = new MailMessage
            {
                From = new MailAddress(_opt.FromAddress, _opt.FromName),
                Subject = subject,
                Body = body,
                IsBodyHtml = false,
            };
            msg.To.Add(to);
            if (!string.IsNullOrWhiteSpace(replyTo)) msg.ReplyToList.Add(new MailAddress(replyTo, replyToName));

            using var client = new SmtpClient();
            if (_opt.Mode.Equals("smtp", StringComparison.OrdinalIgnoreCase))
            {
                client.Host = _opt.SmtpHost;
                client.Port = _opt.SmtpPort;
                client.EnableSsl = _opt.SmtpSsl;
                if (!string.IsNullOrEmpty(_opt.SmtpUser))
                    client.Credentials = new NetworkCredential(_opt.SmtpUser, _opt.SmtpPassword);
            }
            else
            {
                Directory.CreateDirectory(_pickupDir);
                client.DeliveryMethod = SmtpDeliveryMethod.SpecifiedPickupDirectory;
                client.PickupDirectoryLocation = _pickupDir;
            }
            await client.SendMailAsync(msg, ct);
        }
    }
}
