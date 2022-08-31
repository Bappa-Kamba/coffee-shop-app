/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-attahiru-kamba-fsnd.us', // the auth0 domain prefix
    audience: 'udaspicelatte', // the audience set for the auth0 app
    clientId: 'Ap6bp2WuDaGtzM3D7PGjPe9P5DOtorXV', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
