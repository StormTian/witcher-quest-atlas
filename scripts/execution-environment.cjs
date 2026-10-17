const platform={darwin:'macos',linux:'linux',win32:'windows'}[process.platform]||process.platform;
module.exports=process.env.ATLAS_EXECUTION_ENVIRONMENT||(
  process.env.GITHUB_ACTIONS==='true'?`github-actions-${(process.env.RUNNER_OS||platform).toLowerCase()}`:`local-${platform}`
);
