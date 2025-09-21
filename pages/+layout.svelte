<script>
  import "@evidence-dev/tailwind/fonts.css";
  import "../app.css";
  import { EvidenceDefaultLayout } from "@evidence-dev/core-components";
  import { base } from "$app/paths"; // Import base path
  export let data;
</script>

<EvidenceDefaultLayout
  {data}
  logo="{base}/tipscout-logo.png"
  hideSidebar={true}
  hideBreadcrumbs={true}
  hideTOC={true}
  neverShowQueries={true}
  githubRepo="https://github.com/kiliantscherny/tipscout"
>
  <slot slot="content" />
</EvidenceDefaultLayout>
