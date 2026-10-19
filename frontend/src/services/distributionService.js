/**
 * Distribution service for circular delivery tracking.
 * With email dispatch decoupled from CircularRoute, active distribution
 * records are maintained downstream.
 */
export async function getDistribution() {
  return {
    timeline: [],
    rows: [],
  };
}
