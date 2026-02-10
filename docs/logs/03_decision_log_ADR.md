# Decision Log (ADR)

## ADR-001: Split v1 baseline and v2 modernisation
**Decision:** Keep operational workflow (v1) separate from analytics (v2).  
**Reason:** Prevent credibility concerns and keep the narrative clear.  
**Consequence:** Some duplication of docs, but reviewers can validate each layer independently.

## ADR-002: Synthetic data only
**Decision:** Use only synthetic data.  
**Reason:** Portfolio safety and privacy.  
**Consequence:** Document assumptions so distributions look realistic.

## ADR-003: Dashboard exports as PNG
**Decision:** Store dashboard evidence as **generated PNG exports** rather than a PBIX-only deliverable.  
**Reason:** PNGs are easy to review, version, and keep portfolio-safe.  
**Consequence:** Provide scripts + page index so exports can be regenerated.
