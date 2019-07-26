#include <assert.h>
#include <common/msg_queue.h>
#include <common/utils.h>
#include <wire/wire.h>

struct msg_queue {
	const u8 **q;
};

struct msg_queue *msg_queue_new(const tal_t *ctx)
{
	struct msg_queue *q = tal(ctx, struct msg_queue);
	q->q = tal_arr(q, const u8 *, 0);
	return q;
}

static void do_enqueue(struct msg_queue *q, const u8 *add TAKES)
{
	tal_arr_expand(&q->q, tal_dup_arr(q, u8, add, tal_count(add), 0));

	/* In case someone is waiting */
	io_wake(q);
}

size_t msg_queue_length(const struct msg_queue *q)
{
	return tal_count(q->q);
}

void msg_enqueue(struct msg_queue *q, const u8 *add)
{
	assert(fromwire_peektype(add) != MSG_PASS_FD);
	do_enqueue(q, add);
}

void msg_enqueue_fd(struct msg_queue *q, int fd)
{
	u8 *fdmsg = tal_arr(q, u8, 0);
	towire_u16(&fdmsg, MSG_PASS_FD);
	towire_u32(&fdmsg, fd);
	do_enqueue(q, take(fdmsg));
}

const u8 *msg_dequeue(struct msg_queue *q)
{
	size_t n = tal_count(q->q);
	const u8 *msg;

	if (!n)
		return NULL;

	msg = q->q[0];
	memmove(q->q, q->q + 1, sizeof(*q->q) * (n-1));
	tal_resize(&q->q, n-1);
	return msg;
}

int msg_extract_fd(const u8 *msg)
{
	const u8 *p = msg + sizeof(u16);
	size_t len = tal_count(msg) - sizeof(u16);

	if (fromwire_peektype(msg) != MSG_PASS_FD)
		return -1;

	return fromwire_u32(&p, &len);
}

void msg_wake(const struct msg_queue *q)
{
	io_wake(q);
}
