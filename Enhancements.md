# Potential Enhancements

## Modules

### Create

- [solace_queue_template](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/queueTemplate)
- [solace_authentication_oauth_provider](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/authenticationOauthProvider)
- [solace_authorization_group](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/authorizationGroup/getMsgVpnAuthorizationGroups)
- [solace_jndi](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/jndi)
- [solace_replay_log](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replayLog)
- [solace_replicated_topic](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/replicatedTopic)
- [solace_topic_endpoint_template](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/topicEndpointTemplate)
- [solace_virtual_hostname](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/virtualHostname)

### Create get_&lt;module> modules

Create remaining *_get_* module for each module.

### Update

  * [solace_rdp_rest_consumer_trusted_cn](https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/restDeliveryPoint/getMsgVpnRestDeliveryPointRestConsumerTlsTrustedCommonNames)
    - deprecated since 2.17 - replaced by "Common Name validation has been replaced by Server Certificate Name validation".

## Solace Cloud Modules

- solace_cloud_user
- solace_cloud_event_portal
---
The End.
