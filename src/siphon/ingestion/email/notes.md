# SMTP-to-HTTP Bridge for Siphon (Receive-Only)

Perfect choice! A receive-only SMTP server is much simpler than full email hosting. You just need to catch emails and funnel them into your existing SiphonServer pipeline.

## **High-Level Architecture**

```
Internet Email → Your SMTP Server (Port 25) → Parse Email → POST to SiphonServer → Standard Pipeline
```

**Key principle**: SMTP server acts as a simple gateway - it receives, parses, and immediately forwards to your existing FastAPI infrastructure.

## **Core Components**

### **1. Lightweight SMTP Daemon**
**Purpose**: Listen on port 25, accept emails, trigger processing
**Options**:
- **Postfix** (most reliable, battle-tested)
- **OpenSMTPD** (simpler, OpenBSD project)
- **Custom Python SMTP server** (ultimate control)

### **2. Email Parser Script**
**Purpose**: Convert raw email to structured data for your API
**Tasks**:
- Extract headers, body, attachments
- Convert to JSON format
- POST to SiphonServer `/email/process` endpoint

### **3. SiphonServer Email Endpoint**
**Purpose**: Receive parsed email data, create ProcessedContent
**Integration**: Fits into your existing `server/run.py`

## **Postfix Configuration Strategy**

### **Minimal Postfix Setup (Receive-Only)**
- **No outbound mail**: Disable all sending capabilities
- **Local delivery only**: Don't relay for other domains
- **Custom transport**: Route all emails to your parser script
- **No user accounts**: No actual mailboxes, just processing

### **Configuration Approach**:
1. **Accept emails** for `ingest@yourdomain.com`
2. **Immediately pipe** to your parser script
3. **Parser script** POSTs to SiphonServer
4. **Discard original** after successful processing

## **Email Processing Pipeline**

### **Step 1: SMTP Receipt**
- Email arrives at your server
- Postfix accepts it (validates basic format)
- Immediately triggers your parser script

### **Step 2: Email Parsing**
- **Extract metadata**: From, To, Subject, Date, Message-ID
- **Process body**: Plain text + HTML content
- **Handle attachments**: Extract files, encode as base64
- **Create email object**: Structured data for your API

### **Step 3: SiphonServer Integration**
- **POST to `/email/process`** with parsed email data
- **Route attachments** through existing file processors
- **Create ProcessedContent** with EmailMetadata
- **Standard enrichment** (titles, summaries, descriptions)

### **Step 4: Error Handling**
- **Log failed emails** for manual review
- **Retry logic** for temporary SiphonServer failures
- **Dead letter queue** for permanently failed emails

## **Data Flow Example**

### **Incoming Email**:
```
From: user@example.com
To: ingest@yourdomain.com
Subject: Important Document
Body: Please process this document
Attachment: report.pdf
```

### **Parsed Format to SiphonServer**:
```json
{
  "message_id": "abc123@example.com",
  "from_address": "user@example.com", 
  "to_addresses": ["ingest@yourdomain.com"],
  "subject": "Important Document",
  "body_text": "Please process this document",
  "body_html": "<p>Please process this document</p>",
  "attachments": [
    {
      "filename": "report.pdf",
      "content_type": "application/pdf",
      "base64_data": "JVBERi0xLjQK..."
    }
  ],
  "received_at": "2024-01-15T10:30:00Z"
}
```

### **SiphonServer Processing**:
1. **Create EmailMetadata** from headers
2. **Process body text** as main content
3. **Route PDF attachment** through MarkItDown
4. **Combine** email + attachment content
5. **Generate** title/description/summary
6. **Store** in PostgreSQL + ChromaDB

## **Infrastructure Requirements**

### **Network Setup**:
- **Public IP**: For receiving emails
- **Port 25 open**: SMTP standard port
- **MX record**: Points `yourdomain.com` to your server IP
- **Reverse DNS**: IP resolves back to your domain

### **DNS Configuration**:
```
yourdomain.com.     MX 10 mail.yourdomain.com.
mail.yourdomain.com. A  203.0.113.10
```

### **Server Security**:
- **Firewall**: Only allow port 25 + your SiphonServer ports
- **No open relay**: Only accept mail for your domains
- **Rate limiting**: Prevent email bombing
- **Fail2ban**: Block malicious senders

## **Operational Benefits**

### **Simplicity**:
- **No user management**: No actual email accounts
- **No storage**: Emails processed and discarded
- **No sending**: No outbound mail complexity
- **No webmail**: No user interfaces needed

### **Integration with Siphon**:
- **Uses existing pipeline**: Email becomes another content type
- **Leverages file processing**: Attachments flow through current handlers
- **Standard enrichment**: Same AI processing as other content
- **Unified search**: Emails indexed with everything else

### **Reliability**:
- **Simple failure modes**: Either email arrives or it doesn't
- **Easy monitoring**: Check SMTP logs + SiphonServer logs
- **Quick recovery**: Restart services independently
- **No data loss**: Failed emails can be replayed

## **Scaling Considerations**

### **Email Volume**:
- **Low volume**: Simple script processing is fine
- **Medium volume**: Queue processing for attachments
- **High volume**: Async processing with job queues

### **Attachment Handling**:
- **Small files**: Process inline with email
- **Large files**: Save to disk, process async via ContextCall
- **Many attachments**: Parallel processing through existing pipeline

### **Server Placement**:
- **Same server as SiphonServer**: Simplest setup
- **Dedicated email server**: Better if high volume
- **Load balancing**: Multiple MX records for reliability

## **Monitoring & Maintenance**

### **Key Metrics**:
- **Emails received**: Volume and frequency
- **Processing success rate**: SiphonServer integration health
- **Attachment processing**: File type success rates
- **Error rates**: Failed parsing or processing

### **Log Analysis**:
- **SMTP logs**: Email receipt and basic validation
- **Parser logs**: Email parsing success/failures
- **SiphonServer logs**: ProcessedContent creation
- **Error logs**: Failed emails for manual review

### **Maintenance Tasks**:
- **Log rotation**: Keep disk usage under control
- **Security updates**: Keep Postfix updated
- **DNS monitoring**: Ensure MX records are working
- **Reputation monitoring**: Check if your IP gets blacklisted

## **Why This Approach is Perfect for Siphon**

### **Architectural Fit**:
- **Leverages existing infrastructure**: Uses your FastAPI server
- **Maintains consistency**: Email content flows through same enrichment
- **Preserves flexibility**: Can add email-specific processing later
- **Clean separation**: SMTP gateway vs. content processing

### **Operational Advantages**:
- **Real-time processing**: No polling delays
- **Direct integration**: Native API calls to your system
- **Full control**: No third-party API limitations
- **Cost effective**: No per-email charges

### **Future Extensibility**:
- **Multiple ingest addresses**: Different processing rules
- **Email threading**: Link related emails together  
- **Sender analytics**: Track communication patterns
- **Smart routing**: Different processing based on sender/subject

This setup gives you a professional email ingestion system that's perfectly tailored to your Siphon architecture. You get the benefits of direct email delivery with minimal operational complexity.

# Security considerations
# Security for SMTP-to-Siphon Email Ingestion

Given you're forwarding from **work Outlook** and **personal Gmail**, security is critical. You're potentially exposing sensitive corporate and personal data, so this needs to be bulletproof.

## **Core Security Principles**

### **1. Assume Emails Contain Sensitive Data**
- **Work emails**: Corporate secrets, PII, confidential communications
- **Personal emails**: Financial info, medical records, private conversations
- **Attachments**: Documents with sensitive content
- **Metadata**: Communication patterns, contact information

### **2. Defense in Depth**
Multiple security layers so that if one fails, others protect you.

### **3. Principle of Least Privilege**
Your SMTP server should do the absolute minimum required to function.

## **Network Security**

### **Firewall Configuration**
```
ALLOW: Port 25 (SMTP) from anywhere
ALLOW: Your SiphonServer ports (8001) from localhost only
ALLOW: SSH (22) from your IP ranges only
DENY: Everything else
```

### **SMTP Server Hardening**
- **No open relay**: Only accept mail for your specific domains
- **Rate limiting**: Prevent email bombing attacks
- **Connection limits**: Limit concurrent SMTP connections
- **Reject invalid**: Drop malformed emails immediately
- **No authentication**: Don't allow anyone to send through your server

### **DNS Security**
- **SPF records**: Prevent domain spoofing
- **DMARC policy**: Monitor for email abuse
- **Secure DNS**: Use DNS over HTTPS/TLS for lookups

## **Access Control & Authentication**

### **Server Access**
- **SSH key authentication only**: No password login
- **VPN access**: Consider requiring VPN for SSH
- **Multi-factor authentication**: If using password managers
- **Sudo logging**: Track all administrative actions

### **Email Address Security**
- **Dedicated domain**: Don't use your main domain
- **Obscure addresses**: Use non-obvious email addresses
- **Multiple addresses**: Different addresses for work vs. personal
- **Address rotation**: Change addresses periodically

### **Example Setup**:
```
work-ingest-2024@yoursiphondomain.com     # Work Outlook forwards here
personal-ingest-2024@yoursiphondomain.com # Gmail forwards here
backup-ingest@yoursiphondomain.com        # Backup address
```

## **Data Protection**

### **Encryption at Rest**
- **Disk encryption**: Full disk encryption on your server
- **Database encryption**: Encrypt PostgreSQL data
- **File system encryption**: Encrypt attachment storage
- **Backup encryption**: Encrypted backups with separate keys

### **Encryption in Transit**
- **TLS for SMTP**: Force encrypted connections
- **HTTPS for API**: Secure SiphonServer communication
- **SSH tunneling**: Encrypt all administrative access

### **Data Minimization**
- **Immediate processing**: Don't store raw emails longer than necessary
- **Selective forwarding**: Only forward emails you actually need processed
- **Attachment filtering**: Skip processing of highly sensitive file types
- **Content redaction**: Strip sensitive data before storage

## **SMTP Server Hardening**

### **Postfix Security Configuration**
- **Disable unnecessary features**: No SASL, no relaying, no user accounts
- **Strict parsing**: Reject malformed emails
- **Content filtering**: Basic malware/spam detection
- **Size limits**: Prevent huge email attacks
- **Connection throttling**: Slow down potential attackers

### **Process Isolation**
- **Run as non-root**: Postfix runs as dedicated user
- **Chroot jail**: Isolate SMTP processes
- **Resource limits**: CPU/memory limits on email processing
- **Separate parsing**: Run email parser as different user

### **Example Security Settings**:
```
# Postfix main.cf security settings
smtpd_helo_required = yes
smtpd_delay_reject = yes
smtpd_recipient_restrictions = reject_invalid_hostname, reject_unknown_recipient_domain
message_size_limit = 25600000  # 25MB limit
mailbox_size_limit = 0         # No local storage
smtpd_client_connection_count_limit = 10
smtpd_client_rate_limit = 30
```

## **Email Processing Security**

### **Input Validation**
- **Email header validation**: Sanitize all email headers
- **Content scanning**: Basic malware detection on attachments
- **File type restrictions**: Only process known-safe file types
- **Size limits**: Prevent resource exhaustion attacks

### **Attachment Security**
- **Virus scanning**: Scan all attachments before processing
- **Sandboxed processing**: Process attachments in isolated environment
- **File type whitelist**: Only allow specific attachment types
- **Content analysis**: Check for embedded malware

### **Parser Security**
- **Input sanitization**: Clean all email content before API calls
- **Error handling**: Don't expose system details in error messages
- **Resource limits**: Prevent parser from consuming too much CPU/memory
- **Logging**: Log all processing attempts for audit

## **Corporate Data Compliance**

### **Work Email Considerations**
- **Data residency**: Check if work data must stay in specific countries
- **Retention policies**: How long can you keep work emails?
- **Access controls**: Who can access processed work content?
- **Audit logging**: Track all access to work-related content

### **Legal Protections**
- **Terms of service**: Document your data handling practices
- **Privacy policy**: Explain how email data is processed
- **Data processing agreements**: If others access the system
- **Incident response plan**: What to do if data is compromised

## **Monitoring & Alerting**

### **Security Monitoring**
- **Failed login attempts**: Alert on SSH brute force
- **Unusual email patterns**: High volume, strange senders
- **Processing errors**: Failed email parsing attempts
- **Resource usage**: CPU/memory/disk alerts

### **Audit Logging**
- **All email processing**: Who sent what when
- **System access**: All SSH logins and sudo commands
- **API access**: All requests to SiphonServer
- **Data access**: Who queried what content

### **Incident Response**
- **Automated alerting**: Real-time notifications for security events
- **Log aggregation**: Centralized logging for analysis
- **Backup procedures**: Regular, tested backups
- **Recovery planning**: How to restore after compromise

## **Operational Security**

### **Regular Maintenance**
- **Security updates**: Keep all software updated
- **Log rotation**: Prevent disk space issues
- **Certificate renewal**: Automate SSL/TLS certificate updates
- **Access review**: Regularly audit who has access

### **Backup Strategy**
- **Encrypted backups**: All backups encrypted at rest
- **Offline copies**: Some backups stored offline
- **Recovery testing**: Regularly test backup restoration
- **Geographic distribution**: Backups in multiple locations

### **Network Isolation**
- **Separate VLANs**: Isolate email server from other services
- **Jump hosts**: Require bastion host for access
- **VPN access**: All management through VPN
- **Network monitoring**: Monitor all network traffic

## **Specific Recommendations for Your Setup**

### **Work Email Security**
1. **Check corporate policies**: Ensure forwarding is allowed
2. **Use dedicated work address**: `work-ingest@yourdomain.com`
3. **Selective forwarding**: Only forward non-confidential emails
4. **Regular audit**: Review what work content is stored
5. **Compliance documentation**: Document your security measures

### **Personal Email Security**
1. **Separate processing**: Keep work and personal data isolated
2. **Use different addresses**: `personal-ingest@yourdomain.com`
3. **Content filtering**: Skip processing of financial/medical emails
4. **Regular cleanup**: Periodically purge old personal data

### **Hybrid Architecture**
```
Work Outlook → work-ingest@domain.com → Separate processing pipeline
Personal Gmail → personal-ingest@domain.com → Separate processing pipeline
```

Both pipelines can use the same infrastructure but maintain logical separation.

## **Emergency Procedures**

### **If Security is Compromised**
1. **Immediately stop email processing**
2. **Disconnect server from internet**
3. **Preserve logs for forensic analysis**
4. **Notify relevant parties** (work IT, personal contacts)
5. **Rebuild from clean backups**

### **Preventive Measures**
- **Intrusion detection**: Monitor for unusual activity
- **File integrity monitoring**: Detect unauthorized changes
- **Regular security scans**: Vulnerability assessments
- **Penetration testing**: Professional security testing

This security framework gives you enterprise-grade protection for your email ingestion system. The key is implementing multiple layers so that even if one security control fails, others will protect your data.
