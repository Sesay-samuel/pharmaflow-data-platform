# PharmaFlow AWS Security Hardening

## Overview

This Terraform module defines AWS security controls for the
PharmaFlow Data Engineering Platform.

The configuration is intended for local validation and
security architecture demonstration.

## Security Components

### AWS KMS
- Customer-managed encryption key
- Automatic key rotation enabled
- 30-day key deletion window
- Dedicated key alias
- IAM-based permission delegation

### AWS CloudTrail
- Multi-region audit trail
- Global service events included
- Log-file integrity validation
- Dedicated S3 audit bucket

### S3 Audit Storage
- Public access blocked
- Server-side encryption using SSE-S3
- Versioning enabled
- HTTPS-only bucket policy
- 90-day current-object expiration
- Noncurrent version expiration after 30 days

### AWS Secrets Manager
- Database secret resource definition
- No database passwords stored in Terraform
- 30-day recovery window

### IAM
- Database-secret read policy
- Access scoped to the designated secret
- Policy not attached to an application role

## Validation

Run:

    terraform init -backend=false
    terraform fmt -check
    terraform validate

## Deployment Status

This module has been validated locally.

Resources have not been deployed to AWS.

Deployment requires a separate security, IAM,
operational and cost review.

## Cost Considerations

Deploying KMS, Secrets Manager, CloudTrail and
S3 audit storage may introduce AWS charges.

AWS Budgets alerts are notifications, not
hard spending limits.
