# 代码片段库

这里收集了 Claude Code 开发中常用的代码片段和模板。

## 📚 目录

- [Skills 开发片段](#skills-开发片段)
- [Agents 开发片段](#agents-开发片段)
- [MCP Servers 开发片段](#mcp-servers-开发片段)
- [常用配置模板](#常用配置模板)
- [测试片段](#测试片段)

---

## Skills 开发片段

### 基本 Skill 结构

#### TypeScript
```typescript
#!/usr/bin/env node
import { Skill } from '@anthropic-ai/sdk';

const skill = new Skill({
  name: 'my-skill',
  description: 'Description of what this skill does',
  version: '1.0.0',
  author: 'Your Name',
});

skill.execute(async (input) => {
  // Parse input parameters
  const { param1, param2 } = input;

  // Skill logic here
  const result = await doSomething(param1, param2);

  // Return result
  return {
    success: true,
    data: result,
  };
});

skill.run();
```

#### Python
```python
#!/usr/bin/env python3
from anthropic import Skill
import asyncio

skill = Skill(
    name="my-skill",
    description="Description of what this skill does",
    version="1.0.0",
    author="Your Name",
)

@skill.execute()
async def execute(input_data):
    # Parse input parameters
    param1 = input_data.get("param1")
    param2 = input_data.get("param2")

    # Skill logic here
    result = await do_something(param1, param2)

    # Return result
    return {
        "success": True,
        "data": result,
    }

if __name__ == "__main__":
    skill.run()
```

### 带 CLI 参数的 Skill
```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import { Skill } from '@anthropic-ai/sdk';

const program = new Command();

program
  .name('my-skill')
  .description('My custom skill')
  .version('1.0.0')
  .option('-f, --file <path>', 'Input file path')
  .option('-o, --output <path>', 'Output file path')
  .option('--verbose', 'Verbose output');

program.parse();
const options = program.opts();

const skill = new Skill({
  name: 'my-skill',
  description: 'Skill with CLI parameters',
  version: '1.0.0',
});

skill.execute(async () => {
  if (options.verbose) {
    console.log('Processing with verbose output...');
  }

  const result = await processFile(options.file, options.output);

  return { success: true, data: result };
});

skill.run();
```

---

## Agents 开发片段

### 基本 Agent 结构
```typescript
import { Agent } from '@anthropic-ai/agent-sdk';

interface AgentState {
  step: number;
  context: Record<string, any>;
}

class MyAgent extends Agent<AgentState> {
  constructor() {
    super({
      name: 'my-agent',
      initialState: {
        step: 0,
        context: {},
      },
    });
  }

  protected async decide(state: AgentState): Promise<AgentState> {
    // Decision-making logic
    const action = this.determineNextAction(state);

    // Execute action
    const result = await this.executeAction(action);

    // Update state
    return {
      ...state,
      step: state.step + 1,
      context: { ...state.context, ...result },
    };
  }

  private determineNextAction(state: AgentState): string {
    // Logic to determine next action based on state
    if (state.step === 0) return 'initialize';
    if (state.context.error) return 'retry';
    return 'proceed';
  }

  private async executeAction(action: string): Promise<any> {
    // Action execution logic
    switch (action) {
      case 'initialize':
        return await this.initialize();
      case 'retry':
        return await this.retry();
      case 'proceed':
        return await this.proceed();
      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }

  private async initialize() {
    // Initialization logic
  }

  private async retry() {
    // Retry logic
  }

  private async proceed() {
    // Proceed logic
  }
}

// Usage
const agent = new MyAgent();
await agent.run();
```

### Agent with Memory
```typescript
import { Agent, MemoryStore } from '@anthropic-ai/agent-sdk';

class AgentWithMemory extends Agent {
  private memory: MemoryStore;

  constructor() {
    super();
    this.memory = new MemoryStore({
      maxSize: 1000, // Maximum number of memories
      ttl: 3600000,  // Time to live in ms
    });
  }

  protected async decide(state: any) {
    // Retrieve relevant memories
    const relevantMemories = await this.memory.query({
      context: state.currentContext,
      limit: 5,
    });

    // Make decision based on memories
    const decision = this.makeDecision(state, relevantMemories);

    // Store experience
    await this.memory.store({
      context: state.currentContext,
      action: decision,
      outcome: state.outcome,
      timestamp: Date.now(),
    });

    return decision;
  }
}
```

### Multi-Agent System
```typescript
import { Agent, AgentOrchestrator } from '@anthropic-ai/agent-sdk';

// Define individual agents
class AnalyzerAgent extends Agent {
  async execute(input: any) {
    // Analysis logic
    return { analysis: '...' };
  }
}

class ValidatorAgent extends Agent {
  async execute(input: any) {
    // Validation logic
    return { valid: true, errors: [] };
  }
}

class ExecutorAgent extends Agent {
  async execute(input: any) {
    // Execution logic
    return { result: '...' };
  }
}

// Orchestrate multiple agents
class MultiAgentSystem extends AgentOrchestrator {
  constructor() {
    super();
    this.registerAgent('analyzer', new AnalyzerAgent());
    this.registerAgent('validator', new ValidatorAgent());
    this.registerAgent('executor', new ExecutorAgent());
  }

  async process(input: any) {
    // Agent chain: analyzer -> validator -> executor
    const analysis = await this.agents.analyzer.execute(input);
    const validation = await this.agents.validator.execute(analysis);

    if (!validation.valid) {
      throw new Error(validation.errors.join(', '));
    }

    const result = await this.agents.executor.execute(validation);

    return result;
  }
}

// Usage
const system = new MultiAgentSystem();
const result = await system.process(inputData);
```

---

## MCP Servers 开发片段

### 基本 MCP Server 结构
```typescript
import { MCPServer } from '@modelcontextprotocol/sdk/server';

const server = new MCPServer({
  name: 'my-mcp-server',
  version: '1.0.0',
});

// Define a Tool
server.addTool({
  name: 'get_data',
  description: 'Fetch data from external API',
  inputSchema: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Search query',
      },
    },
    required: ['query'],
  },
  handler: async (input) => {
    const data = await fetchDataFromAPI(input.query);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(data, null, 2),
      }],
    };
  },
});

// Define a Resource
server.addResource({
  uri: 'file:///config.json',
  name: 'Configuration',
  description: 'Server configuration',
  mimeType: 'application/json',
  handler: async () => {
    const config = await loadConfig();
    return {
      contents: [{
        uri: 'file:///config.json',
        mimeType: 'application/json',
        text: JSON.stringify(config, null, 2),
      }],
    };
  },
});

// Define a Prompt
server.addPrompt({
  name: 'summarize',
  description: 'Summarize the given content',
  arguments: [
    {
      name: 'content',
      description: 'Content to summarize',
      required: true,
    },
  ],
  handler: async (args) => {
    return {
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Please summarize the following:\n\n${args.content}`,
          },
        },
      ],
    };
  },
});

// Start server
server.start();
```

### MCP Server with Authentication
```typescript
import { MCPServer, AuthMiddleware } from '@modelcontextprotocol/sdk/server';

const server = new MCPServer({
  name: 'secure-mcp-server',
  version: '1.0.0',
});

// Add authentication middleware
server.use(new AuthMiddleware({
  validateToken: async (token) => {
    // Validate token against your auth system
    const user = await validateTokenWithAuthSystem(token);
    return user;
  },
  onUnauthorized: (req) => {
    return {
      error: 'Unauthorized',
      message: 'Invalid or missing token',
    };
  },
}));

// Protected tool
server.addTool({
  name: 'sensitive_operation',
  description: 'Perform sensitive operation',
  inputSchema: {
    type: 'object',
    properties: {
      data: { type: 'string' },
    },
    required: ['data'],
  },
  handler: async (input, context) => {
    // Access authenticated user from context
    const user = context.user;

    // Execute operation with user context
    const result = await performSensitiveOperation(input.data, user);

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result),
      }],
    };
  },
});

server.start();
```

---

## 常用配置模板

### Claude Code 配置 (claude.json)
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost:5432/dbname"]
    }
  },
  "skills": {
    "directory": "~/.claude/skills",
    "autoUpdate": true
  },
  "hooks": {
    "pre-commit": "~/.claude/hooks/pre-commit.sh",
    "post-commit": "~/.claude/hooks/post-commit.sh"
  }
}
```

### Skill Package.json
```json
{
  "name": "claude-skill-my-skill",
  "version": "1.0.0",
  "description": "My custom Claude Code skill",
  "main": "index.js",
  "bin": {
    "my-skill": "./cli.js"
  },
  "scripts": {
    "start": "node cli.js",
    "test": "jest",
    "lint": "eslint ."
  },
  "keywords": [
    "claude-code",
    "skill",
    "cli"
  ],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "@anthropic-ai/sdk": "^1.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }
}
```

---

## 测试片段

### Skill 测试
```typescript
import { MySkill } from './my-skill';
import { TestContext } from '@anthropic-ai/sdk/testing';

describe('MySkill', () => {
  let skill: MySkill;
  let context: TestContext;

  beforeEach(() => {
    skill = new MySkill();
    context = new TestContext();
  });

  test('should process input correctly', async () => {
    const input = { param1: 'test', param2: 42 };

    const result = await skill.execute(input);

    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
  });

  test('should handle errors gracefully', async () => {
    const input = { param1: null, param2: null };

    const result = await skill.execute(input);

    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});
```

### Agent 测试
```typescript
import { MyAgent } from './my-agent';
import { MockAgentRuntime } from '@anthropic-ai/agent-sdk/testing';

describe('MyAgent', () => {
  let agent: MyAgent;
  let runtime: MockAgentRuntime;

  beforeEach(() => {
    agent = new MyAgent();
    runtime = new MockAgentRuntime();
  });

  test('should make correct decisions', async () => {
    const initialState = { step: 0, context: {} };

    const finalState = await runtime.run(agent, initialState);

    expect(finalState.step).toBeGreaterThan(0);
    expect(finalState.context).toHaveProperty('result');
  });

  test('should handle errors and retry', async () => {
    const stateWithErrors = {
      step: 1,
      context: { error: new Error('Test error') }
    };

    const resultState = await agent.decide(stateWithErrors);

    expect(resultState.context.error).toBeNull();
  });
});
```

### MCP Server 测试
```typescript
import { MCPServer, MockClient } from '@modelcontextprotocol/sdk/testing';

describe('My MCPServer', () => {
  let server: MCPServer;
  let client: MockClient;

  beforeAll(async () => {
    server = new MCPServer({ name: 'test-server', version: '1.0.0' });
    await server.start();

    client = new MockClient(server);
  });

  afterAll(async () => {
    await server.stop();
  });

  test('should execute tool correctly', async () => {
    const result = await client.callTool('my_tool', { param: 'value' });

    expect(result.content[0].type).toBe('text');
    expect(result.content[0].text).toBeDefined();
  });

  test('should return resource', async () => {
    const result = await client.getResource('file:///test.json');

    expect(result.contents[0].uri).toBe('file:///test.json');
    expect(result.contents[0].text).toBeDefined();
  });
});
```

---

## 贡献指南

如果你有有用的代码片段，欢迎贡献！

1. Fork 本仓库
2. 创建新的片段文件
3. 添加清晰的注释和说明
4. 提交 Pull Request

---

**最后更新**: 2025-12-30
