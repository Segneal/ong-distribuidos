import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { getAuthToken } from './api';

// HTTP link para GraphQL
const httpLink = createHttpLink({
  uri: process.env.REACT_APP_GRAPHQL_URL || 'http://localhost:3001/api/graphql',
});

// Auth link para incluir el token JWT
const authLink = setContext((_, { headers }) => {
  const token = getAuthToken();
  return {
    headers: {
      ...headers,
      ...(token && { authorization: `Bearer ${token}` }),
    }
  };
});

// Cliente Apollo
const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          donationReport: {
            merge: false, // Always replace the cache with new data
          },
          eventParticipationReport: {
            merge: false, // Always replace the cache with new data
          },
          savedDonationFilters: {
            merge: false, // Always replace the cache with new data
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-and-network',
    },
    query: {
      errorPolicy: 'all',
      fetchPolicy: 'cache-and-network',
    },
    mutate: {
      errorPolicy: 'all',
    },
  },
});

export default apolloClient;