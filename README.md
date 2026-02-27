# UK Farm Blog

Live at **https://www.britfarmers.com**

## Namecheap DNS Setup

Add the following records in the Namecheap **Advanced DNS** panel for `britfarmers.com`:

### Required records

| Type  | Host | Value                          | TTL        |
|-------|------|--------------------------------|------------|
| CNAME | www  | `vtsochev45-web.github.io`     | Automatic  |
| A     | @    | `185.199.108.153`              | Automatic  |
| A     | @    | `185.199.109.153`              | Automatic  |
| A     | @    | `185.199.110.153`              | Automatic  |
| A     | @    | `185.199.111.153`              | Automatic  |

The four `A` records point the bare/apex domain (`britfarmers.com`) to GitHub Pages
so visitors who omit the `www.` are redirected automatically.  The `CNAME` record
points the `www` subdomain to GitHub Pages, which matches the `CNAME` file
committed in this repository.

### After updating DNS

1. Wait for propagation (usually a few minutes, up to 48 hours).
2. In the GitHub repository go to **Settings → Pages → Custom domain**, enter
   `www.britfarmers.com`, and save.  GitHub will verify the DNS and issue a
   free TLS certificate automatically.
3. Tick **Enforce HTTPS** once the certificate has been provisioned.

