## Loyalty Card Distributed Service

### Table of contents
- [Description](#description)
- [Architecture](#architecture)
- [Use cases](#use-cases)
- [Serverless functions](#serverless-functions)

### Description
This project implements a distributed loyalty card service. Users gain points with every purchase and they are able to redeem their points in discounts. Every account can be shared among up to 4 persons, and the points gathered are redeemable in every store immediately.

### Architecture
The distributed service is designed using the serverless application model to offer scalability and high availability. It is deployed on AWS and leverages the following runtime components:
- **API Gateway**: User requests are directed to an API gateway. The API gateway acts as a load balancer, distributing user requests to lambda function instances.
- **Lambda functions**: AWS Lambda is a serverless computing service. For every user request, API gateway invokes a new Lambda function instance. As every user request is handled by a different instance, Lambda is ideal for handling peaks in traffic.
- **DynamoDB**: DynamoDB is a managed NoSQL database.
- **Cognito**: Amazon Cognito is a service managing user sign-up and authentication. Registered users can authenticate with their credentials and get a JWT access token to access the protected endpoints.

### Use cases
The distributed service implements the following use cases:
1. A new user is registered and becomes a member of a group.
2. A user makes a purchase and earns points.
3. A user retrieves their purchase history and points.
4. A user redeems points for a discount.

### Serverless functions
The following Lambda functions are implemented. Every function exposes an API endpoint.
- ```registerUser(username, password, groupId) –> status```  
An endpoint to register a new user and add them to a group. If the groupId is None, a new group is created.
- ```loginUser(username, password) –> token```  
This endpoint verifies user credentials and returns an access token if they are correct.
- ```getPurchaseHistory(groupId) –> list[dict]```  
This endpoint returns the purchase history for a specific group.
- ```registerPurchase(userId, groupId, purchaseId, purchaseValue) -> status```  
This endpoint registers a new purchase. If the purchase identifier already exists in the database, no changes are made. It also converts the purchase value to points and updates the relevant database table.
- ```getPoints(groupId) –> dict```  
An endpoint to retrieve the number of points that a group currently has.
- ```redeemPoints(groupId, points, redemptionId) –> status```  
An endpoint to redeem points for a specific groupId. If the redemptionId is already in the database, no changes are made. If there are not enough to redeem, the endpoint returns an appropriate message.
