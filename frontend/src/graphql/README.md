# GraphQL Configuration

This directory contains the GraphQL configuration for the ONG Management System reports functionality.

## Structure

- `apollo.js` - Apollo Client configuration with authentication and caching
- `donations.js` - Queries and mutations for donation reports and filters
- `events.js` - Queries for event participation reports
- `types.js` - GraphQL fragments and input type definitions
- `utils.js` - Utility functions for error handling and data cleaning
- `index.js` - Main export file for all GraphQL operations

## Configuration

### Apollo Client Setup

The Apollo Client is configured with:
- JWT authentication via Authorization header
- Optimized caching policies for reports data
- Error handling for network and GraphQL errors
- Cache-and-network fetch policy for fresh data

### Environment Variables

Required environment variables:
- `REACT_APP_GRAPHQL_URL` - GraphQL endpoint URL (default: http://localhost:3000/api/graphql)

### API Endpoints

The GraphQL endpoint `/api/graphql` is proxied through the API Gateway to the reports service.

## Usage

### Importing Operations

```javascript
import { 
  GET_DONATION_REPORT, 
  SAVE_DONATION_FILTER,
  GET_EVENT_PARTICIPATION_REPORT 
} from '../graphql';
```

### Using in Components

```javascript
import { useQuery, useMutation } from '@apollo/client';
import { GET_DONATION_REPORT } from '../graphql';

const { data, loading, error } = useQuery(GET_DONATION_REPORT, {
  variables: { categoria: 'ALIMENTOS' }
});
```

### Error Handling

```javascript
import { getGraphQLErrorMessage, isAuthError } from '../graphql';

if (error) {
  const message = getGraphQLErrorMessage(error);
  if (isAuthError(error)) {
    // Handle authentication error
  }
}
```

## Available Operations

### Queries
- `GET_DONATION_REPORT` - Fetch donation reports with filtering
- `GET_SAVED_DONATION_FILTERS` - Fetch saved donation filters
- `GET_EVENT_PARTICIPATION_REPORT` - Fetch event participation reports
- `GET_USERS_LIST` - Fetch users list for filtering

### Mutations
- `SAVE_DONATION_FILTER` - Save a new donation filter
- `UPDATE_DONATION_FILTER` - Update existing donation filter
- `DELETE_DONATION_FILTER` - Delete a donation filter