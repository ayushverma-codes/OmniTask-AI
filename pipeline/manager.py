import os
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from pipeline.workflow import build_graph

async def process_request(thread_id: str, text: str, file_path: str | None) -> str:
    os.makedirs("artifact", exist_ok=True)
    db_path = "artifact/checkpoints.sqlite"

    conn = None
    try:
        # 1. Manual Connection
        conn = await aiosqlite.connect(db_path)
        # 2. Patch is_alive
        conn.is_alive = lambda: True 

        # 3. Setup Persistence
        checkpointer = AsyncSqliteSaver(conn)
        await checkpointer.setup()

        # 4. Compile Graph
        graph = build_graph()
        app = graph.compile(checkpointer=checkpointer)

        # 5. Load Previous State
        config = {"configurable": {"thread_id": thread_id}}
        current_state = await app.aget_state(config)
        
        # 6. Preserve File Path Logic
        existing_file = None
        if current_state and current_state.values:
            existing_file = current_state.values.get("current_file_path")

        path_to_use = file_path if file_path else existing_file

        # 7. Create Input (Note: extracted_content is handled internally by the graph state)
        input_state = {
            "messages": [{"role": "user", "content": text}],
            "current_file_path": path_to_use
        }

        # 8. Run
        final_state = await app.ainvoke(input_state, config=config)

        # 9. Return
        if final_state and "messages" in final_state and final_state["messages"]:
            last_msg = final_state["messages"][-1]
            return last_msg["content"]
        
        return "Error: No response generated."

    except Exception as e:
        return f"Pipeline Error: {str(e)}"
        
    finally:
        if conn:
            await conn.close()