# NextGen Mirth Connect

[Mirth Connect](https://github.com/nextgenhealthcare/connect) NextGen Connect Integration Engine (historically and still widely known as Mirth Connect) is the leading healthcare integration engine used to filter, transform, route, and exchange critical data between disparate clinical and administrative systems. Acting as a "Swiss Army knife" for healthcare interoperability, it acts as a translator to ensure different medical platforms can seamlessly communicate.

## Roadmap

``` shell
[ Edan iM3 Monitor ] ──(HL7 v2 Message via TCP/IP)──> [ Mirth Connect Listener ]
                                                              │
                                            (Validates / Auto-Acknowledges)
                                                              ▼
                                                   [ Your Local Destination ]
                                              (Database, Webhook, FHIR API, etc.)
```

## Author Information

Maintained by **Jared Cook** as part of the core infrastructure and container management ecosystem.

<!--
## Author Notes Hidden:

# TODO:
    * research: https://github.com/metriport/metriport
-->
