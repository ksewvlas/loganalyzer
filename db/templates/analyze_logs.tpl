SELECT
    project_id,
    status,
    count(DISTINCT remote_addr) AS unique_users,
    sum(body_bytes_sent) AS total_bytes_sent,
    count(status) AS total_requests,
    count(DISTINCT http_referer) AS referrers
FROM (
    SELECT * FROM logs
    WHERE project_id = {{ pid }}
        AND time_local BETWEEN '{{ from_ }}' AND '{{ to_ }}'
    GROUP BY id
) project_logs
GROUP BY project_id, status
