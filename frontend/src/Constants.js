const production = {
  url: window.location.protocol + '//' + window.location.hostname + ':8000',
};

const development = {
  url: window.location.protocol + '//' + window.location.hostname + ':8000',
};

export const config =
  process.env.REACT_APP_IP === 'development' ? development : production;
